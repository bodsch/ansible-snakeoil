import pytest
import os
import yaml
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


@pytest.fixture()
def AnsibleDefaults():
    with open("../../defaults/main.yml", 'r') as stream:
        return yaml.load(stream)


#@pytest.mark.parametrize("dirs", [
#    "/tmp/deployment_artefacts"
#])
#def test_directories(host, dirs):
#    d = host.file(dirs)
#    assert d.is_directory
#    assert d.exists
#
#
#@pytest.mark.parametrize("files", [
#    "/tmp/deployment_artefacts/snakeoil.tgz"
#])
#def test_files(host, files):
#    f = host.file(files)
#    assert f.exists
#    assert f.is_file


#def test_user(host):
#    assert host.group("coremedia").exists
#    assert host.user("coremedia").exists
