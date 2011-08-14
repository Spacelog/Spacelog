Vagrant::Config.run do |config|
  config.vm.box = "ubuntu-1104-server-i386"
  config.vm.box_url = "http://dl.dropbox.com/u/7490647/talifun-ubuntu-11.04-server-i386.box"
  config.vm.network "172.16.1.2"
  config.vm.share_folder("v-root", "/vagrant", ".", :nfs => true)
  config.vm.provision :chef_solo do |chef|
   chef.cookbooks_path = "chef"
   chef.add_recipe "spacelog"
  end
end
