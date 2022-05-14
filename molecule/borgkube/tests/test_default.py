
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

import json
import pytest
import os
import ssl
# from molecule import util

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def pp_json(json_thing, sort=True, indents=2):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


def base_directory():
    cwd = os.getcwd()

    if('group_vars' in os.listdir(cwd)):
        directory = "../.."
        molecule_directory = "."
    else:
        directory = "."
        molecule_directory = "molecule/{}".format(os.environ.get('MOLECULE_SCENARIO_NAME'))

    return directory, molecule_directory


@pytest.fixture()
def get_vars(host):
    """

    """
    base_dir, molecule_dir = base_directory()
    distribution = host.system_info.distribution

    if distribution in ['debian', 'ubuntu']:
        os = "debian"
    elif distribution in ['redhat', 'ol', 'centos', 'rocky', 'almalinux']:
        os = "redhat"
    elif distribution in ['arch']:
        os = "archlinux"

    print(" -> {} / {}".format(distribution, os))

    file_defaults = "file={}/defaults/main.yml name=role_defaults".format(base_dir)
    file_vars = "file={}/vars/main.yml name=role_vars".format(base_dir)
    file_molecule = "file={}/group_vars/all/vars.yml name=test_vars".format(molecule_dir)
    file_distibution = "file={}/vars/{}.yaml name=role_distibution".format(base_dir, os)

    defaults_vars = host.ansible("include_vars", file_defaults).get("ansible_facts").get("role_defaults")
    vars_vars = host.ansible("include_vars", file_vars).get("ansible_facts").get("role_vars")
    distibution_vars = host.ansible("include_vars", file_distibution).get("ansible_facts").get("role_distibution")
    molecule_vars = host.ansible("include_vars", file_molecule).get("ansible_facts").get("test_vars")

    ansible_vars = defaults_vars
    ansible_vars.update(vars_vars)
    ansible_vars.update(distibution_vars)
    ansible_vars.update(molecule_vars)

    templar = Templar(loader=DataLoader(), variables=ansible_vars)
    result = templar.template(ansible_vars, fail_on_undefined=False)

    return result


def test_directories(host, get_vars):
    """
    """
    wanted_domain = get_vars.get("snakeoil_domain", None)

    dirs = [
        "/etc/ssl/{0}"
    ]

    for directory in dirs:
        d = host.file(directory.format(wanted_domain))
        assert d.is_directory


def test_files(host, get_vars):
    """
    """
    wanted_domain = get_vars.get("snakeoil_domain", None)

    files = [
        "/etc/ssl/{0}/dh.pem",
        "/etc/ssl/{0}/{0}.conf",
        "/etc/ssl/{0}/{0}.crt",
        "/etc/ssl/{0}/{0}.csr",
        "/etc/ssl/{0}/{0}.key",
        "/etc/ssl/{0}/{0}.pem",
    ]

    for file in files:
        f = host.file(file.format(wanted_domain))
        assert f.exists


def test_cert(host, get_vars):
    """
    """
    wanted_alt_names = get_vars.get("snakeoil_alt_names", [])
    wanted_domain = get_vars.get("snakeoil_domain", None)
    # print(" - {} -> {}".format(wanted_domain, wanted_alt_names))
    if len(wanted_alt_names) > 0:
        """
        """
        cert_file_name = os.path.join(
            get_vars.get("snakeoil_local_tmp_directory"),
            wanted_domain,
            f"{wanted_domain}.pem")

        if os.path.exists(cert_file_name):
            try:
                cert_dict = ssl._ssl._test_decode_cert(cert_file_name)
            except Exception as e:
                assert "Error decoding certificate: {0:}".format(e)
            else:
                # get all alternative names
                alt_names = cert_dict.get("subjectAltName")
                # convert tuple to dict
                alt_names = dict(map(reversed, alt_names))
                # print(f"found in certificate: {alt_names}")
                # seperate values
                alt_dns = [k for k, v in alt_names.items() if v == "DNS"]
                alt_ips = [k for k, v in alt_names.items() if v == "IP Address"]
                # print(f"DNS: {alt_dns}")
                # print(f"IP : {alt_ips}")
                for n in wanted_alt_names:
                    dns = n.get("dns", [])
                    ip = n.get("ip", [])
                    # assert for all DNS entries
                    for d in dns:
                        assert d in alt_dns
                    # assert for all IP entries
                    for i in ip:
                        assert i in alt_ips
        else:
            assert False, f"file {cert_file_name} is not present on ansible controller"
