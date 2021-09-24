#  (C) Copyright Wieger Wesselink 2020. Distributed under the GPL-3.0-or-later
#  Software License, (See accompanying file LICENSE or copy at
#  https://www.gnu.org/licenses/gpl-3.0.txt)

class IdentifierGenerator(object):
    def __init__(self, index: int = 0):
        self.index = index

    def generate(self, hint):
        id = '{}{}'.format(hint, self.index)
        self.index = self.index + 1
        return id