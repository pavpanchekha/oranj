from pygments.lexer import RegexLexer, bygroups, using
from pygments.token import *
from pygments.lexers import PythonLexer
from pygments.lexers.web import XmlLexer

class OranjLexer(RegexLexer):
    name = "Oranj"
    aliases = ["oranj", "or"]
    filenames = ["*.or"]

    tokens = {
        "root": [
            (r"[a-zA-Z0-9\$_]+(?=\s*=\s*fn)", Name.Function),
            (r"[a-zA-Z0-9\$_]+(?=\s*=\s*class)", Name.Class),
            (r"\s+|;+", Whitespace),
            (r"\b((is\s+not)|(aint)|mod|and|or|not|in|is)\b", Operator.Word),
            (r"[\./\+\-\*\|\^]", Operator),
            (r"(?<![<>])(\+|\-|\^|\/|\/\/|\*|<<|>>)\=(?![=<>])", Operator),
            (r"(?<![<>])\=(?![=<>])", Operator),
            (r"[><!]|==", Operator),
            (r"true|false|nil|inf", Keyword.Constant),
            (r"self|block|runtime", Keyword.Psuedo),
            (r"[\[\{\(\)\}\]\,]", Punctuation),
            (r"\b(catch|class|else|elif|finally|for|fn|yield|if|return|throw|try|while|with|del|extern|import|break|continue|assert|as)\b", Keyword.Reserved),
            (r"""(?<![\.eE]|\d)(?:(?:[ \t]*[0-9])+)(?![ \t]*\.|\d|\w)""", Number.Integer),
            (r"""(?<![\.eE]|\d)(?:0(?:\w))(?:(?:[ \t]*[0-9a-zA-Z])+)(?![ \t]*\.|\d|\w)""", Number.Integer),
            (r"(?P<number>(?:(?:[ \t]*[0-9])+\.(?:[ \t]*[0-9])+)|(?:\.(?:[ \t]*[0-9])+)|(?:(?:[ \t]*[0-9])+\.))(?P<exponent>(?:[eE][+-]?(?:[ \t]*[0-9])*)?)", Number.Float),
            (r"$$[a-zA-Z0-9\$_]+", Name.Function),
            (r"(?P<value>[a-zA-Z0-9\$_]+)", Name.Variable),

            (r"#!", Comment.Preproc, "procdir"),
            (r"\#.*", Comment),

            #(r"""[a-z]*((['"])(?:\2\2)?)(?:\\\2|[^\1])*?\1""", String),
            (r"'", String, "string1"),
            (r'"', String, "string2"),
            (r"'''", String, "string3"),
            (r'"""', String, "string6"),
        ],

        "procdir": [
            (r"python\s*{", Comment.Preproc, "python"),
            (r"xml\s*{", Comment.Preproc, "xml"),
            (r"[a-zA-Z0-9]+(\s.*)?\n", Comment.Preproc, "#pop"),
            (r".*", Comment, "#pop"),
        ],

        "string1": [
            (r"\\.", String.Escape),
            (r"'", String, "#pop"),
            (r".", String),
        ],

        "string2": [
            (r"\\.", String.Escape),
            (r'"', String, "#pop"),
            (r".", String),
        ],

        "string3": [
            (r"\\.", String.Escape),
            (r"'''", String, "#pop"),
            (r".", String),
        ],

        "string6": [
            (r"\\.", String.Escape),
            (r'"""', String, "#pop"),
            (r".", String),
        ],

        "python": [
            (r"\s*#!\s*}", Comment.Preproc, "#pop"),
            (r".*\n", using(PythonLexer)),
        ],

        "xml": [
            (r"\s*#!\s*}", Comment.Preproc, "#pop"),
            (r".*\n", using(XmlLexer)),
        ],
    }
