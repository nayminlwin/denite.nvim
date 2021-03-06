# ============================================================================
# FILE: matcher/clap.py
# AUTHOR: Shougo Matsushita <Shougo.Matsu at gmail.com>
# License: MIT license
# ============================================================================

import sys
from pathlib import Path

from denite.base.filter import Base
from denite.util import Nvim, UserContext, Candidates, convert2fuzzy_pattern


class Filter(Base):

    def __init__(self, vim: Nvim) -> None:
        super().__init__(vim)

        self.name = 'matcher/clap'
        self.description = 'clap matcher'
        self.vars = {
            'clap_path': '',
        }

        self._initialized = False
        self._disabled = False

    def filter(self, context: UserContext) -> Candidates:
        if not context['candidates'] or not context[
                'input'] or self._disabled or not self.vars['clap_path']:
            return context['candidates']  # type: ignore

        if not self._initialized:
            # vim-clap installation check
            ext = '.pyd' if context['is_windows'] else '.so'
            clap_path = Path('{}/pythonx/clap/fuzzymatch_rs{}'.format(
                self.vars['clap_path'], ext))
            if clap_path.exists():
                # Add path
                sys.path.append(str(clap_path.parent))
                self._initialized = True
            else:
                self.error_message(context,
                                   'matcher/clap: ' + str(clap_path) +
                                   ' is not found in your runtimepath.')
                self._disabled = True
                return []

        result = self._get_clap_result(
            context['candidates'], context['input'],
            int(context['max_candidate_width']))
        d = {x['word']: x for x in context['candidates']}
        return [d[x] for x in result[1]]

    def convert_pattern(self, input_str: str) -> str:
        return convert2fuzzy_pattern(input_str)

    def _get_clap_result(self, candidates: Candidates,
                         pattern: str, winwidth: int) -> Candidates:
        import fuzzymatch_rs
        return fuzzymatch_rs.fuzzy_match(   # type: ignore
            pattern, tuple((d['word'] for d in candidates)),
            winwidth, False, 'Full')
