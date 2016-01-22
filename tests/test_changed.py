# # -*- coding: utf-8 -*-
# import os
#
# from yamldirs import create_files
#
# from dkfileutils.changed import changed
#
#
# def xtest_dirchange():
#     files = """
#         - foo:
#             - bar
#     """
#     with create_files(files) as directory:
#         os.chdir(directory)
#         count = 0
#         print os.listdir('.')
#         print os.listdir('foo')
#         with changed.changed_dir('foo'):
#             count += 1
#         assert count == 1
#         # changed_dir with no changes messes with the trace function..
#         # try:  # pragma: nocover
#         #     with changed.changed_dir('foo'):
#         #         count += 1
#         # except Exception as e:
#         #     pass
#         # assert count == 1
