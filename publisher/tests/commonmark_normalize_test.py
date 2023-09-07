from typing import Any, TextIO
import re
import logging
import unittest

from common.log import configure_logging

import roampub.commonmark_normalize as norm

class CommonMarkNormalizeTests(unittest.TestCase):

    def test_normalize_block_content(self):
        input: str = (
            """
            ```javascript
            __results__ = []
        
            for (number=1; number<=100; number++) {
            
            """
        )
        self.assertEqual(norm.normalize_block_content(input), input)

        input: str =  "In this age of __affordable__ beauty there was something __heraldic__ about his __lack__ of it."
        output: str =  "In this age of *affordable* beauty there was something *heraldic* about his *lack* of it."
        self.assertEqual(norm.normalize_block_content(input), output)

        input: str =  ">hello\r\n\r\n\r\ncruel\r\n\r\n\r\n\nworld"
        output: str = ">hello\n>\n>cruel\n>\n>world"
        self.assertEqual(norm.normalize_block_content(input), output)

        input: str =  ">hello\r\n\r\n\r\n__cruel__\r\n\r\n\r\n\nworld"
        output: str = ">hello\n>\n>*cruel*\n>\n>world"
        self.assertEqual(norm.normalize_block_content(input), output)


    def test_normalize_code_block(self):
        input: str = (
            """
            ```javascript
            __results__ = []
        
            for (number=1; number<=100; number++) {
            
            """
        )
        self.assertEqual(
            norm.normalize_code_block(norm.CODE_BLOCK_RULE, input), norm.NormalizationResult(input, True))

        input: str = (
            """
            __```javascript
            results = []
        
            for (number=1; number<=100; number++) {
            
            """
        )
        self.assertEqual(
            norm.normalize_code_block(norm.CODE_BLOCK_RULE, input), norm.NormalizationResult(input, False))
        
        input: str = (
            """
            ```javascript
            results = []
        
            for (number=1; number<=100; number++) {
            
            """
        )
        self.assertEqual(
            norm.normalize_code_block(norm.CODE_BLOCK_RULE, input), norm.NormalizationResult(input, True))

        input: str = (
            """
            ```javascript
            results = []
        
            for (number=1; number<=100; number++) {
            ```
            """
        )
        self.assertEqual(
            norm.normalize_code_block(norm.CODE_BLOCK_RULE, input), norm.NormalizationResult(input, True))
        
        input: str =  "In this age of __affordable__ beauty there was something __heraldic__ about his __lack__ of it."
        self.assertEqual(
            norm.normalize_code_block(norm.CODE_BLOCK_RULE, input), norm.NormalizationResult(input, False))
        input: str =  "__hello cruel __world"
        self.assertEqual(
            norm.normalize_code_block(norm.CODE_BLOCK_RULE, input), norm.NormalizationResult(input, False))
        input: str =  ">hello world"
        self.assertEqual(
            norm.normalize_code_block(norm.CODE_BLOCK_RULE, input), norm.NormalizationResult(input, False))
        input: str =  "hello world"
        self.assertEqual(
            norm.normalize_code_block(norm.CODE_BLOCK_RULE, input), norm.NormalizationResult(input, False))


    def test_normalize_italic(self):
        input: str =  "hello world"
        self.assertEqual(
            norm.normalize_italics(norm.ITALICS_RULE, input), norm.NormalizationResult(input, False))
        input: str =  "__hello world"
        self.assertEqual(
            norm.normalize_italics(norm.ITALICS_RULE, input), norm.NormalizationResult(input, False))
        input: str =  "hello__world"
        self.assertEqual(
            norm.normalize_italics(norm.ITALICS_RULE, input), norm.NormalizationResult(input, False))
        input: str =  "hello world__"
        self.assertEqual(
            norm.normalize_italics(norm.ITALICS_RULE, input), norm.NormalizationResult(input, False))
        input: str =  "__hello__ world"
        output: str = "*hello* world"
        self.assertEqual(
            norm.normalize_italics(norm.ITALICS_RULE, input), norm.NormalizationResult(output, False))
        input: str =  "__hello cruel __world"
        output: str =  "*hello cruel *world"
        self.assertEqual(
            norm.normalize_italics(norm.ITALICS_RULE, input), norm.NormalizationResult(output, False))
        input: str =  "__hello__ cruel __world__"
        output: str =  "*hello* cruel *world*"
        self.assertEqual(
            norm.normalize_italics(norm.ITALICS_RULE, input), norm.NormalizationResult(output, False))
        input: str =  "In this age of __affordable__ beauty there was something __heraldic__ about his __lack__ of it."
        output: str =  "In this age of *affordable* beauty there was something *heraldic* about his *lack* of it."
        self.assertEqual(
            norm.normalize_italics(norm.ITALICS_RULE, input), norm.NormalizationResult(output, False))
        input: str =  "If the number is evenly divisible by 3, print __'Fizz'__ instead of the number"
        output: str =  "If the number is evenly divisible by 3, print *'Fizz'* instead of the number"
        self.assertEqual(
            norm.normalize_italics(norm.ITALICS_RULE, input), norm.NormalizationResult(output, False))


    def test_italic_replace(self):
        content: str = "In this age of __affordable beauty__ there was something heraldic about his __lack__ of it."
        updated: str = re.sub(norm.ROAM_ITALIC_PATTERN, r"*\1*", content)
        self.assertEqual(
            updated, "In this age of *affordable beauty* there was something heraldic about his *lack* of it."
        )

        content: str = "In this age of __affordable beauty__ there was something heraldic about his lack of it."
        updated: str = re.sub(norm.ROAM_ITALIC_PATTERN, r"*\1*", content)
        self.assertEqual(
            updated, "In this age of *affordable beauty* there was something heraldic about his lack of it."
        )


    def test_italic_pattern(self):

        content: str = """three rings for the elven kings under the sky.
        5 for the dwarf __lords__ in their halls of stone
        """
        matched: re.Match = re.search(norm.ROAM_ITALIC_PATTERN, content)  # type: ignore
        logging.debug(f"matched: {matched.group(1)}")
        self.assertEqual(matched.span(), (71, 80))
        self.assertEqual(matched.span(1), (73, 78))
        self.assertEqual(matched.group(1), 'lords')

        matched: re.Match = re.search(norm.ROAM_ITALIC_PATTERN, "__hello __")  # type: ignore
        logging.debug(f"matched: {matched}")
        self.assertEqual(matched.span(), (0, 10))

        matched: re.Match = re.search(norm.ROAM_ITALIC_PATTERN, "__hello__")  # type: ignore
        logging.debug(f"matched: {matched}")
        self.assertEqual(matched.span(), (0, 9))

        self.assertIsNone(re.search(norm.ROAM_ITALIC_PATTERN, "**hello**"))
        self.assertIsNone(re.search(norm.ROAM_ITALIC_PATTERN, "_hello_"))
        self.assertIsNone(re.search(norm.ROAM_ITALIC_PATTERN, "__hello\n__"))
        self.assertIsNone(re.search(norm.ROAM_ITALIC_PATTERN, "__\r\n__"))
        self.assertIsNone(re.search(norm.ROAM_ITALIC_PATTERN, "__\n\r__"))
        self.assertIsNone(re.search(norm.ROAM_ITALIC_PATTERN, "__\r__"))
        self.assertIsNone(re.search(norm.ROAM_ITALIC_PATTERN, "__\n__"))
        self.assertIsNone(re.search(norm.ROAM_ITALIC_PATTERN, "__"))
        self.assertIsNone(re.search(norm.ROAM_ITALIC_PATTERN, "____"))
        self.assertIsNone(re.search(norm.ROAM_ITALIC_PATTERN, "hello world"))


    def test_normalize_block_quote(self):
        input: str =  "hello world"
    
        self.assertEqual(
            norm.normalize_block_quote(norm.BLOCK_QUOTE_RULE, input), norm.NormalizationResult(input, False))
        input: str =  "\nhello world"
        self.assertEqual(
            norm.normalize_block_quote(norm.BLOCK_QUOTE_RULE, input), norm.NormalizationResult(input, False))
        input: str =  "hello\nworld"
        self.assertEqual(
            norm.normalize_block_quote(norm.BLOCK_QUOTE_RULE, input), norm.NormalizationResult(input, False))
        input: str =  "hello world\n"
        self.assertEqual(
            norm.normalize_block_quote(norm.BLOCK_QUOTE_RULE, input), norm.NormalizationResult(input, False))
        input: str =  ">hello\n\nworld"
        output: str = ">hello\n>\n>world"
        self.assertEqual(
            norm.normalize_block_quote(norm.BLOCK_QUOTE_RULE, input), norm.NormalizationResult(output, False))
        input: str =  ">hello\n\ncruel\n\nworld"
        output: str =  ">hello\n>\n>cruel\n>\n>world"
        self.assertEqual(
            norm.normalize_block_quote(norm.BLOCK_QUOTE_RULE, input), norm.NormalizationResult(output, False))
        input: str =  ">hello\n\n\ncruel\n\n\n\nworld"
        output: str = ">hello\n>\n>cruel\n>\n>world"
        self.assertEqual(
            norm.normalize_block_quote(norm.BLOCK_QUOTE_RULE, input), norm.NormalizationResult(output, False))
        input: str =  ">hello\r\n\r\n\r\ncruel\r\n\r\n\r\n\nworld"
        output: str = ">hello\n>\n>cruel\n>\n>world"
        self.assertEqual(
            norm.normalize_block_quote(norm.BLOCK_QUOTE_RULE, input), norm.NormalizationResult(output, False))


    def test_paragraph_breaks(self):

        input: str =  "hello world"
        self.assertEqual(re.sub(norm.PARA_BREAK_PATTERN, "\n\n>", input), input)
        input: str =  "\nhello world"
        self.assertEqual(re.sub(norm.PARA_BREAK_PATTERN, "\n\n>", input), input)
        input: str =  "hello\nworld"
        self.assertEqual(re.sub(norm.PARA_BREAK_PATTERN, "\n\n>", input), input)
        input: str =  "hello world\n"
        self.assertEqual(re.sub(norm.PARA_BREAK_PATTERN, "\n\n>", input), input)
        input: str =  "hello\n\nworld"
        output: str = "hello\n\n>world"
        self.assertEqual(re.sub(norm.PARA_BREAK_PATTERN, "\n\n>", input), output)
        input: str =  "hello\n\ncruel\n\nworld"
        output: str = "hello\n\n>cruel\n\n>world"
        self.assertEqual(re.sub(norm.PARA_BREAK_PATTERN, "\n\n>", input), output)
        input: str =  "hello\n\n\ncruel\n\n\n\nworld"
        output: str = "hello\n\n>cruel\n\n>world"
        self.assertEqual(re.sub(norm.PARA_BREAK_PATTERN, "\n\n>", input), output)
        input: str =  "hello\r\n\r\n\r\ncruel\r\n\r\n\r\n\nworld"
        output: str = "hello\n\n>cruel\n\n>world"
        self.assertEqual(re.sub(norm.PARA_BREAK_PATTERN, "\n\n>", input), output)

        self.assertSequenceEqual(re.findall(norm.PARA_BREAK_PATTERN, "hello world"), [])
        self.assertSequenceEqual(re.findall(norm.PARA_BREAK_PATTERN, "\nhello world"), [])
        self.assertSequenceEqual(re.findall(norm.PARA_BREAK_PATTERN, "hello\nworld"), [])
        self.assertSequenceEqual(re.findall(norm.PARA_BREAK_PATTERN, "hello world\n"), [])
        self.assertSequenceEqual(re.findall(norm.PARA_BREAK_PATTERN, "hello world\n\n"), [])
    
        found: iterator[re.Match] = re.finditer(norm.PARA_BREAK_PATTERN, "hello\n\nworld")  # type: ignore
        logging.debug(f"found: {found}")
        matched: re.Match = next(found)
        logging.debug(f"matched: {matched}")
        self.assertEqual(matched.span(), (5,7))
        self.assertEqual(matched.group(), "\n\n")
        with self.assertRaises(StopIteration):
            matched: re.Match = next(found)

        found: iterator[re.Match] = re.finditer(norm.PARA_BREAK_PATTERN, "hello\n\ncruel\n\nworld")  # type: ignore
        logging.debug(f"found: {found}")
        matched: re.Match = next(found)
        logging.debug(f"matched: {matched}")
        self.assertEqual(matched.span(), (5,7))
        self.assertEqual(matched.group(), "\n\n")
        matched: re.Match = next(found)
        logging.debug(f"matched: {matched}")
        self.assertEqual(matched.span(), (12,14))
        self.assertEqual(matched.group(), "\n\n")
        with self.assertRaises(StopIteration):
            matched: re.Match = next(found)

        self.assertIsNone(re.search(norm.PARA_BREAK_PATTERN, "hello world"))
        self.assertIsNone(re.search(norm.PARA_BREAK_PATTERN, "\nhello world"))
        self.assertIsNone(re.search(norm.PARA_BREAK_PATTERN, "hello\nworld"))
        self.assertIsNone(re.search(norm.PARA_BREAK_PATTERN, "hello\nworld\n"))
        self.assertIsNone(re.search(norm.PARA_BREAK_PATTERN, "hello world\n"))
        self.assertIsNone(re.search(norm.PARA_BREAK_PATTERN, "hello world\n\n"))

        matched: re.Match = re.search(norm.PARA_BREAK_PATTERN, "hello\n\nworld")  # type: ignore
        logging.debug(f"matched: {matched}")
        self.assertEqual(matched.span(), (5,7))

        matched: re.Match = re.search(norm.PARA_BREAK_PATTERN, "hello\n\n\nworld")  # type: ignore
        logging.debug(f"matched: {matched}")
        self.assertEqual(matched.span(), (5,8))

        matched: re.Match = re.search(norm.PARA_BREAK_PATTERN, "hello\r\n\r\nworld")  # type: ignore
        logging.debug(f"matched: {matched}")
        self.assertEqual(matched.span(), (5,9))

        para_break_pattern: str = r"[\n]"

        matched: re.Match = re.search(r"wo", "hello world")  # type: ignore
        logging.debug(f"matched: {matched}")
        self.assertEqual(matched.span(), (6,8))

        matched: re.Match = re.search(para_break_pattern, "\nhello world")  # type: ignore
        logging.debug(f"matched: {matched}")
        self.assertEqual(matched.span(), (0,1))

        matched: re.Match = re.search(para_break_pattern, "hello\nworld")  # type: ignore
        logging.debug(f"matched: {matched}")
        self.assertEqual(matched.span(), (5,6))

        matched: re.Match = re.search(para_break_pattern, "hello world\n\n")  # type: ignore
        logging.debug(f"matched: {matched}")
        self.assertEqual(matched.span(), (11,12))



    def setUp(self):
        configure_logging(logging.DEBUG)
        logging.debug("logging configured")


if __name__ == '__main__':
    unittest.main()