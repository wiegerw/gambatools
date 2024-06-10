#  (C) Copyright Wieger Wesselink 2024. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

from gambatools.global_settings import GambaTools


def log(*args, **kwargs):
    if GambaTools.enable_logging:
        print(*args, **kwargs)
