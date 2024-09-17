import subprocess
import os
import sys

from backend.api import Mission, Act, LogLine
from backend.util import redis_connection, seconds_to_timestamp


class StatsPornGenerator(object):
    width = 901
    height = 78
    key_scene_marker_files = 'backend/stats_porn_assets/key_scene_%d.png'
    max_bar_height = 40
    graph_background_width = 896
    graph_bar_colour = '#00a9d2'
    end_marker_colour = '#989898'

    image_output_path = 'missions/%s/images/stats/'

    def __init__(self, redis_conn):
        self.redis_conn = redis_conn

    def build_all_missions(self):
        for mission in list(Mission.Query(self.redis_conn)):
            self.build_mission(mission)

    def build_mission(self, mission):
        print("Building data visualisations for %s..." % mission.name)
        for act in list(Act.Query(self.redis_conn, mission.name)):
            print(' ... %s' % act.title)

            # Split the act into sections, one for each bar on the graph
            act_duration = act.end - act.start
            section_duration = act_duration // 92
            
            # Count the number of log lines in each segment
            # and find the maximum number of log lines in a segment
            t = act.start
            segment_line_counts = []
            max_line_count = 0
            real_output_path = self.image_output_path % mission.name
            while t < act.end:
                # Load log lines for this segment
                query = LogLine.Query(self.redis_conn, mission.name).transcript(mission.main_transcript).range(t, t+section_duration)
                line_count = len(list(query))
                # Store segment stats
                max_line_count = max(line_count, max_line_count)
                segment_line_counts.append((t, t+section_duration, line_count))
                t += section_duration

            # Make sure we have an output directory and work out where to
            # write the image
            try:
                os.makedirs(real_output_path)
            except OSError:
                pass
            graph_file = 'graph_%s.png' % act.number
            output_path = '%s/%s' % (real_output_path, graph_file)

            # Add initial draw command
            draw_commands = [
                'convert',
                '-size', '%dx%d' % (self.width, self.height), 'xc:transparent',
                '-fill', self.end_marker_colour,
                '-draw', "path 'M 1,1  L 10,1  L 5,8  L 1,1",
                '-draw', "path 'M 890,1  L 900,1  L 895,8  L 890,1",
                '-fill', self.graph_bar_colour,
            ]

            # Add initial image map tags
            image_map_id = '%s_%s_frequency_graph' % (mission.name, act.number)
            image_map = ['<map id="%s" name="%s">' % (image_map_id, image_map_id)]

            # Iterate over the segments and add them to the draw commands and image map
            for i, line in enumerate(segment_line_counts):
                start, end, count = line
                height = int(round(count / float(max(max_line_count, 1)) * self.max_bar_height))

                bar_width = 6
                bar_spacing = 4

                top_left_x     = i * (bar_width + bar_spacing) + 2
                top_left_y     = self.max_bar_height - height + 14
                bottom_right_x = top_left_x + bar_width
                bottom_right_y = self.max_bar_height + 14

                draw_commands.append('-draw')
                draw_commands.append('rectangle %s,%s,%s,%s' % (top_left_x, top_left_y, bottom_right_x, bottom_right_y))

                if height > 0:
                    image_map.append('<area shape="rect" coords="%(coords)s" href="%(url)s" alt="%(alt)s">' % {
                        "url":    '/%s/%s/#show-selection' % (seconds_to_timestamp(start), seconds_to_timestamp(end)),
                        "alt":    '%d lines between %s and %s' % (count, seconds_to_timestamp(start), seconds_to_timestamp(end)),
                        "coords": '%s,%s,%s,%s' % (top_left_x, top_left_y, bottom_right_x, bottom_right_y),
                    })

            # Output the basic graph image
            draw_commands.append(output_path)
            subprocess.call(draw_commands)

            # Iterate over the key scenes adding them to the graph and image map
            for i, key_scene in enumerate(act.key_scenes()):
                print('     - %s' % key_scene.title)

                top_left_x =     int((self.graph_background_width / float(act_duration)) * (key_scene.start - act.start)) + 2
                top_left_y =     self.max_bar_height + 5 + 14
                bottom_right_x = top_left_x + 20
                bottom_right_y = top_left_y + 20
                marker_image =   self.key_scene_marker_files % (i+1)
                
                subprocess.call([
                    'composite',
                    '-geometry', '+%s+%s' % (top_left_x, top_left_y),
                    marker_image,
                    output_path,
                    output_path,
                ])

                image_map.append('<area shape="rect" coords="%(coords)s" href="%(url)s" alt="%(alt)s">' % {
                    "url":      '/%s/%s/#show-selection' % (seconds_to_timestamp(key_scene.start), seconds_to_timestamp(key_scene.end)),
                    "alt":      key_scene.title,
                    "coords":   '%s,%s,%s,%s' % (top_left_x, top_left_y, bottom_right_x, bottom_right_y),
                })

            # Finalise the image map
            image_map.append('</map>')

            self.redis_conn.hmset(
                'act:%s:%s:stats' % (mission.name, act.number),
                {
                    "image_map":    "\n".join(image_map),
                    "image_map_id": image_map_id,
                }
            )


if __name__ == "__main__":
    generator = StatsPornGenerator(redis_connection)

    selected_missions_to_build = sys.argv[1:]
    if selected_missions_to_build:
        for mission_name in selected_missions_to_build:
            mission = Mission(redis_connection, mission_name)
            generator.build_mission(mission)
    else:
        generator.build_all_missions()
