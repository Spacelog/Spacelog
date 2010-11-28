import subprocess
import redis
import os

from backend.api import Mission, Act, LogLine
from backend.util import seconds_to_timestamp

class StatsPornGenerator(object):
    
    graph_background_file = 'backend/stats_porn_assets/chart_background.png'
    graph_background_height = 40
    graph_bar_colour = '#00a9d2'
    
    image_output_path = 'missions/%s/images/stats/'
    
    def __init__(self, redis_conn):
        self.redis_conn = redis_conn

    def build_all_missions(self):
        for mission in list(Mission.Query(self.redis_conn)):
            self.build_mission(mission)

    def build_mission(self, mission):
        print "Building data visualisations for %s..." % mission.name
        for act in list(Act.Query(self.redis_conn, mission.name)):
            print ' ... %s' % act.title
            section_duration = (act.end - act.start) // 92
            t = act.start            
            segment_line_counts = []
            max_line_count = 0
            real_output_path = self.image_output_path % mission.name
            while t < act.end:
                query = LogLine.Query(self.redis_conn, mission.name).transcript(mission.main_transcript).range(t, t+section_duration)
                line_count = len(list(query))

                max_line_count = max(line_count, max_line_count)
                segment_line_counts.append((t, t+section_duration, line_count))
                t += section_duration

                try:
                    os.makedirs('%s/%s/stats' % (real_output_path, mission.name))
                except OSError:
                    pass

                graph_file = 'graph_%s_%s.png' % (mission.name, act.number)
                output_path = '%s/%s' % (real_output_path, graph_file)

                draw_commands = ['convert', self.graph_background_file, '-fill', self.graph_bar_colour]

                image_map_id = '%s_%s_frequency_graph' % (mission.name, act.number)
                image_map = ['<map id="%s" name="%s">' % (image_map_id, image_map_id)]

            for i, line in enumerate(segment_line_counts):
                start, end, count = line
                height = int(round(count / float(max_line_count) * self.graph_background_height))
                draw_commands.append('-draw')

                bar_width = 6
                bar_spacing = 4

                top_left_x     = i * (bar_width + bar_spacing)
                top_left_y     = self.graph_background_height-height
                bottom_right_x = top_left_x + bar_width
                bottom_right_y = self.graph_background_height

                draw_commands.append('rectangle %s,%s,%s,%s' % (top_left_x, top_left_y, bottom_right_x, bottom_right_y))
                image_map.append('<area shape="rect" coords="%(coords)s" href="%(url)s" alt="%(alt)s">' % {
                    "url":      '/%s/%s/#show-selection' % (seconds_to_timestamp(start), seconds_to_timestamp(end)),
                    "alt":      '%d lines between %s and %s' % (count, seconds_to_timestamp(start), seconds_to_timestamp(end)),
                    "coords":   '%s,%s,%s,%s' % (top_left_x, top_left_y, bottom_right_x, bottom_right_y),
                })

            draw_commands.append(output_path)
            subprocess.call(draw_commands)

            image_map.append('</map>')

            self.redis_conn.hmset(
                'act:%s:%s:stats' % (mission.name, act.number),
                {
                    "image_map":    "\n".join(image_map),
                    "image_map_id": image_map_id,
                    "image":        '/assets/transcripts/%s' % graph_file,
                }
            )


if __name__ == "__main__":
    redis_conn = redis.Redis()
    generator = StatsPornGenerator(redis_conn)
    generator.build_all_missions()
