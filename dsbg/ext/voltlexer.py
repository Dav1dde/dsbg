from pygments.lexer import inherit
from pygments.lexers.compiled import DLexer
from pygments.token import Keyword, Name


class VoltLexer(DLexer):
    """
    For Volt source.
    """
    name = 'Volt'
    filenames = ['*.volt']
    aliases = ['volt']
    mimetypes = ['text/x-voltsrc']

    tokens = {
        'root': [
            inherit,
            (r'(va_arg|__thread)\b', Keyword
            ),
            (r'(idouble)\b', Keyword.Type
            ),
            (r'(__DATE__|__EOF__|__TIME__|__TIMESTAMP__|__VENDOR__'
             r'|__VERSION__)\b', Keyword.Pseudo
            ),
            (r'(string|wstring|dstring|size_t|ptrdiff_t'
             r'|Error|Exception|Throwable|TypeInfo)\b', Name.Builtin
            )
        ]
    }

# pure hack
__all__ = ['VoltLexer']
def add_lexers(lexers):
    from pygments.lexers._mapping import LEXERS

    for lexer in lexers:
        LEXERS[lexer.__class__.__name__] = (lexer.__module__, lexer.name,
                                            tuple(lexer.aliases),
                                            tuple(lexer.filenames),
                                            tuple(lexer.mimetypes))

add_lexers([VoltLexer])

if __name__ == '__main__':
    from pygments.lexers import get_lexer_by_name
    from pygments.lexers._mapping import LEXERS

    print LEXERS
    print get_lexer_by_name('volt')