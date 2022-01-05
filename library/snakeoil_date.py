#!/usr/bin/python
# -*- coding: utf-8 -*-

# (c) 2021, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, print_function
import os
from datetime import datetime

from ansible.module_utils.basic import AnsibleModule


__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '0.1',
    'status': ['preview'],
    'supported_by': 'community'
}


class SnakeoilDate(object):
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
        self.snakeoil_directory = module.params.get("snakeoil_directory")
        self.snakeoil_domain = module.params.get("snakeoil_domain")
        self.pattern = module.params.get("pattern")

    def run(self):
        """
        """
        result = dict(
            failed=False,
            changed=False,
            expire_date="none",
            diff_days=0
        )

        certificate = os.path.join(self.snakeoil_directory, self.snakeoil_domain, self.snakeoil_domain + ".pem")

        if os.path.isfile(certificate):
            _ssl_args = []
            _ssl_args.append(self._openssl)
            _ssl_args.append("x509")
            _ssl_args.append("-enddate")
            _ssl_args.append("-noout")
            _ssl_args.append("-in")
            _ssl_args.append(certificate)

            rc, out, err = self._exec(_ssl_args)

            if rc == 0:
                date = out.rstrip("\n").split("=")[1]
                _cert_date = datetime.strptime(date, "%b %d %H:%M:%S %Y GMT")
                _current_date = datetime.now()

                diff_days = (_cert_date - _current_date)
                diff_days = diff_days.days

                _cert_date = _cert_date.strftime(self.pattern)

                self.module.log(msg="expire_date  '{}'".format(_cert_date))
                self.module.log(msg="diff days    '{}'".format(diff_days))

                result = dict(
                    failed=False,
                    changed=False,
                    expire_date=_cert_date,
                    diff_days=diff_days
                )

        return result

    def _exec(self, args):
        """
        """
        self.module.log(msg="args: {}".format(args))

        rc, out, err = self.module.run_command(args, check_rc=False)

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
            snakeoil_directory=dict(required=True, type="path"),
            snakeoil_domain=dict(required=True, type="path"),
            pattern=dict(type="str", default="%Y-%m-%dT%H:%M:%S")
        ),
        supports_check_mode=False,
    )

    icingacli = SnakeoilDate(module)
    result = icingacli.run()

    module.log(msg="= result : '{}'".format(result))

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
