Vagrant::Config.run do |config|
  config.vm.box = "debian-squeeze-32"
  config.vm.box_url = "http://mathie-vagrant-boxes.s3.amazonaws.com/debian_squeeze_32.box"
  config.vm.network "172.16.1.2"
  config.vm.share_folder("v-root", "/vagrant", ".", :nfs => true)
  config.vm.provision :chef_solo do |chef|
   chef.cookbooks_path = "chef"
   chef.add_recipe "spacelog"
  end
end
