Vagrant.configure(2) do |config|
  config.vm.box = "trusty-server-cloudimg-amd64-vagrant-disk1"
  config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"

  config.vm.network "private_network", ip: "172.16.1.2"
  config.vm.network "forwarded_port", guest: 8000, host: 8000
  config.vm.network "forwarded_port", guest: 8001, host: 8001

  config.vm.synced_folder ".", "/vagrant", type: "nfs"

  config.vm.provision :chef_solo do |chef|
    chef.cookbooks_path = "chef"
    chef.add_recipe "spacelog"
  end
end
