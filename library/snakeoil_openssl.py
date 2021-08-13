#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2021, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, print_function
import os

from ansible.module_utils.basic import AnsibleModule


__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}


class SnakeoilOpenssl(object):
    """
      Main Class
    """
    module = None

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self._openssl = module.get_bin_path('openssl', True)
        self.state = module.params.get("state")
        self.directory = module.params.get("directory")
        self.domain = module.params.get("domain")
        self.dhparam = module.params.get("dhparam")
        self.cert_life_time = module.params.get("cert_life_time")
        self.openssl_config = module.params.get("openssl_config")

    def run(self):
        """
        """
        result = dict(
            failed=True,
            changed=False,
            msg="failed"
        )

        base_directory = os.path.join(self.directory, self.domain)

        if not os.path.isdir(base_directory):
            return dict(
                failed=True,
                changed=False,
                msg="missing directory {}".format(base_directory)
            )

        os.chdir(base_directory)
        _ssl_args = []

        csr_file = os.path.join(self.directory, self.domain, self.domain + ".csr")
        crt_file = os.path.join(self.directory, self.domain, self.domain + ".crt")
        pem_file = os.path.join(self.directory, self.domain, self.domain + ".pem")
        key_file = os.path.join(self.directory, self.domain, self.domain + ".key")
        dh_file = os.path.join(self.directory, self.domain, "dh.pem")

        if self.state == "csr":
            _ssl_args.append(self._openssl)
            _ssl_args.append("req")
            _ssl_args.append("-new")
            _ssl_args.append("-sha512")
            _ssl_args.append("-nodes")
            _ssl_args.append("-out")
            _ssl_args.append(csr_file)
            _ssl_args.append("-newkey")
            _ssl_args.append("rsa:4096")
            _ssl_args.append("-keyout")
            _ssl_args.append(key_file)
            _ssl_args.append("-config")
            _ssl_args.append(self.openssl_config)

            rc, out, err = self._exec(_ssl_args)

            result = dict(
                failed=False,
                changed=True,
                msg="success"
            )

        if self.state == "crt":
            _ssl_args.append(self._openssl)
            _ssl_args.append("x509")
            _ssl_args.append("-req")
            _ssl_args.append("-in")
            _ssl_args.append(csr_file)
            _ssl_args.append("-out")
            _ssl_args.append(crt_file)
            _ssl_args.append("-signkey")
            _ssl_args.append(key_file)
            _ssl_args.append("-days")
            _ssl_args.append(str(self.cert_life_time))

            rc, out, err = self._exec(_ssl_args)

            # cat {{ domain }}.crt {{ domain }}.key >> {{ domain }}.pem
            if rc == 0:
                filenames = [crt_file, key_file]
                with open(pem_file, 'w') as outfile:
                    for fname in filenames:
                        with open(fname) as infile:
                            outfile.write(infile.read())

            result = dict(
                failed=False,
                changed=True,
                msg="success"
            )

        if self.state == "dhparam":
            _ssl_args.append(self._openssl)
            _ssl_args.append("dhparam")
            _ssl_args.append("-5")
            _ssl_args.append("-out")
            _ssl_args.append(dh_file)
            _ssl_args.append(str(self.dhparam))

            rc, out, err = self._exec(_ssl_args)

            result = dict(
                failed=False,
                changed=True,
                msg="success"
            )

        return result

    def _exec(self, args):
        """
        """
        self.module.log(msg="args: {}".format(args))

        rc, out, err = self.module.run_command(args, check_rc=True)

        self.module.log(msg="  rc : '{}'".format(rc))
        self.module.log(msg="  out: '{}'".format(str(out)))
        self.module.log(msg="  err: '{}'".format(err))

        return rc, out, err


# ===========================================
# Module execution.
#


def main():
    """

    """
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(required=True, choose=['crt', 'csr', 'dhparam']),
            directory=dict(required=True, type="path"),
            domain=dict(required=True, type="path"),
            dhparam=dict(default=1024, type="int"),
            cert_life_time=dict(default=10, type="int"),
            openssl_config=dict(required=False, type="str"),
            # openssl_params=dict(required=True, type="path"),
        ),
        supports_check_mode=False,
    )

    icingacli = SnakeoilOpenssl(module)
    result = icingacli.run()

    module.log(msg="= result : '{}'".format(result))

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
