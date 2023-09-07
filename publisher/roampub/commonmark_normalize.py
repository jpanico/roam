""" functions to convert RoamPub flavored MarkDown (Roam MarkDown as conventionally interpreted by RoamPub) into CommonMark. Uses MarkdownIt for CommonMark conformance.
 
Types:

    NormalizationResult
    Normalization

    
Classes:

    NormalizationRule

    
Functions:

    normalize_block_content(str) -> str

"""
from typing import NamedTuple, TypeAlias, Callable, Final
import logging
import re

from common.log import TRACE

logger = logging.getLogger(__name__)


NormalizationResult = NamedTuple(
    "NormalizationResult", 
    [
        ('normalized_content', str), 
        ('did_consume', bool)
    ]
)


Normalization: TypeAlias = Callable[['NormalizationRule', str], NormalizationResult]


class NormalizationRule(NamedTuple):
    name: str
    description: str
    impl: Normalization


    def normalize(self, content: str) -> NormalizationResult: 
        logger.debug(f"rule: {self}")    
        if not isinstance(content, str):
            raise TypeError()
    
        return self.impl(self, content)
    

PARA_BREAK_PATTERN: re.Pattern = re.compile(r"[\r?\n]{2,}(?=\S)")
ROAM_ITALIC_PATTERN: re.Pattern = re.compile(r"__([^_\r\n]+)__")


def normalize_block_quote(rule: NormalizationRule, content: str) -> NormalizationResult:
    logger.log(TRACE, f"rule: {rule}, content: {content}")

    stripped_content: str = content.strip()
    if not content.startswith('>'):
        return NormalizationResult(content, False)
    
    normalized_content: str =  PARA_BREAK_PATTERN.sub("\n>\n>", stripped_content)
    return NormalizationResult(normalized_content, False)


BLOCK_QUOTE_RULE: Final[NormalizationRule] = NormalizationRule(
    'BlockQuoteRule', 
    (
        "a BlockContentNode that starts `>` is treated as one big block quote, spanning any number of blank lines." +
        "so additional `>` chars are added at paragraph boundaries"
    ), 
    normalize_block_quote
)

def normalize_code_block(rule: NormalizationRule, content: str) -> NormalizationResult:
    logger.log(TRACE, f"rule: {rule}, content: {content}")
    stripped: str = content.strip()
    return NormalizationResult(content, is_code_block(stripped))


CODE_BLOCK_RULE: Final[NormalizationRule] = NormalizationRule(
    'CodeBlockRule', 
    (
        "a BlockContentNode that starts with ``` is treated as one big code block" +
        "Right now, there are no transformations applied by this normalization, but the rule will" +
        "`consume` the block, preventing any other rules from applying"
    ), 
    normalize_code_block
)

def normalize_italics(rule: NormalizationRule, content: str) -> NormalizationResult:
    normalized_content: str =   ROAM_ITALIC_PATTERN.sub(r"*\1*", content)
    return NormalizationResult(normalized_content, False)


ITALICS_RULE: Final[NormalizationRule] = NormalizationRule(
    'ItalicsRule', 
    (
        "In Roam MD, bold == **bold**, and italic == __italic__" +
        "In CommonMark, *emphasis* | _emphasis_, and **strong emphasis** | __strong emphasis__" +
        "This rule follows `Markua` conventions: __italic__ -> *emphasis*; **bold** -> **strong emphasis**"
    ), 
    normalize_italics
)


ALL_RULES: Final[list[NormalizationRule]] = [
    # simply comment out any rules you wish to disable
    CODE_BLOCK_RULE,
    BLOCK_QUOTE_RULE,
    ITALICS_RULE,
]


def normalize_block_content(content: str) -> str:
    logging.debug(f"content: {content}")

    normalized_content: str = content
    for rule in ALL_RULES:
        rule_result: NormalizationResult = rule.normalize(normalized_content)
        normalized_content = rule_result.normalized_content
        if rule_result.did_consume:
            break

    return normalized_content


def is_code_block(content: str) -> bool:
    return content.startswith("```")

