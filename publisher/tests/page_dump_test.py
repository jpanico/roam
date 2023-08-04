from typing import Callable, cast
import logging
import unittest

from common.log import configure_logging

from roampub.roam_model import *
from roampub.page_dump import *

class PageDumpTests(unittest.TestCase):

    def test_create_vertex_map(self):
        pass


    def test_read_page_dump_json(self):
        creative_brief_json: list[dict[str, Any]] = read_page_dump_json("./tests/data/Creative Brief.json")
        logging.debug(f"creative_brief_json: {creative_brief_json}")
        self.assertEqual(len(creative_brief_json),12)
        self.assertEqual(sum(1 for i in creative_brief_json if i['vertex-type'] == VertexType.ROAM_PAGE.value),1)
        self.assertEqual(sum(1 for i in creative_brief_json if i['vertex-type'] == VertexType.ROAM_FILE.value),0)
        self.assertEqual(
            sum(1 for i in creative_brief_json if i['vertex-type'] == VertexType.ROAM_BLOCK_HEADING.value),
            3
        )
        self.assertEqual(
            sum(1 for i in creative_brief_json if i['vertex-type'] == VertexType.ROAM_BLOCK_CONTENT.value),
            8
        )
        first: dict[str, Any] = creative_brief_json[0]
        logging.debug(f"first: {first}")
        self.assertEqual(first['uid'],'lALsKb-Dx')
        self.assertEqual(first['vertex-type'],VertexType.ROAM_PAGE.value)
        self.assertEqual(first['media-type'],MediaType.TEXT_PLAIN.value)
        self.assertEqual(first['text'],'Creative Brief')
        self.assertEqual(first['children'],[
            "C2uKKD4-b",
            "ZdZlJbgy1",
            "6TCv5eKPQ",
            "2bW3xKCMS",
            "4jf3ZlLqF",
            "ZnUfgOM7W",
            "6r7Q5nxw5"
        ])
        self.assertIsNone(first.get('refs'))

        last: dict[str, Any] = creative_brief_json[-1]
        logging.debug(f"last: {last}")
        self.assertEqual(last['uid'],'6r7Q5nxw5')
        self.assertEqual(last['vertex-type'],VertexType.ROAM_BLOCK_CONTENT.value)
        self.assertEqual(last['media-type'],MediaType.TEXT_PLAIN.value)
        self.assertEqual(last['text'],'So every programmer, whether they know it or not, is making a decision each time they write some code-- ')
        self.assertIsNone(last.get('children'))
        self.assertIsNone(last.get('refs'))

        page3_json: list[dict[str, Any]] = read_page_dump_json("./tests/data/Page 3.json")
        logging.debug(f"page3_json: {page3_json}")
        self.assertEqual(len(page3_json),30)
        self.assertEqual(sum(1 for i in page3_json if i['vertex-type'] == VertexType.ROAM_PAGE.value),4)
        self.assertEqual(sum(1 for i in page3_json if i['vertex-type'] == VertexType.ROAM_FILE.value),2)
        self.assertEqual(sum(1 for i in page3_json if i['vertex-type'] == VertexType.ROAM_BLOCK_CONTENT.value),24)

        first: dict[str, Any] = page3_json[0]
        logging.debug(f"first: {first}")
        self.assertEqual(first['uid'],'hfm6NKq2c')
        self.assertEqual(first['vertex-type'],VertexType.ROAM_PAGE.value)
        self.assertEqual(first['media-type'],MediaType.TEXT_PLAIN.value)
        self.assertEqual(first['text'],'Page 3')
        self.assertEqual(first['children'],["IO75SriD8","uFL-CFN6i","LXoC6aV1-","dftwwQg-V"])
        self.assertIsNone(first.get('refs'))

        last: dict[str, Any] = page3_json[-1]
        logging.debug(f"last: {last}")
        self.assertEqual(last['uid'],'mvVww9zGd')
        self.assertEqual(last['vertex-type'],VertexType.ROAM_BLOCK_CONTENT.value)
        self.assertEqual(last['media-type'],MediaType.TEXT_PLAIN.value)
        self.assertEqual(last['text'],'Block 1.2')
        self.assertEqual(last['children'],["Wu-bKjjdJ"])
        self.assertIsNone(last.get('refs'))


    def test_create_roam_vertex(self):
       self._test_create_file_vertex(create_roam_vertex)
       self._test_create_block_content_node(create_roam_vertex)
       self._test_create_block_heading_node(create_roam_vertex)
       self._test_create_page_node(create_roam_vertex)


    def test_create_file_vertex(self):
       self._test_create_file_vertex(create_file_vertex)


    def _test_create_file_vertex(self, creator: Callable[[dict[str, Any]], RoamVertex]):
        file_name: str = "flower.jpeg"
        location: Url = "https://firebasestorage.googleapis.com/v0/b/firescript-577a2.appspot.com/o/imgs%2Fapp%2FSCFH%2F-9owRBegJ8.jpeg.enc?alt=media&token=9b673aae-8089-4a91-84df-9dac152a7f94"
        uid: Uid = "9b673aae-8089-4a91-84df-9dac152a7f94"
        vertex_type: VertexType = VertexType.ROAM_FILE
        vertex_type_value: str = vertex_type.value
        media_type: MediaType = MediaType.IMAGE_JPEG
        media_type_value: str = media_type.value
        source: dict = {
            "file-name": file_name,
            "source": location,
            "uid": uid,
            "vertex-type": vertex_type_value,
            "media-type": media_type_value
        }
        logging.debug(f"source: {source}")
        file_vertext: FileVertex = cast(FileVertex, creator(source))

        logging.debug(f"file_vertext: {file_vertext}")
        self.assertEqual(file_vertext.uid,uid)
        self.assertEqual(file_vertext.vertex_type,vertex_type)
        self.assertEqual(file_vertext.media_type,media_type)
        self.assertEqual(file_vertext.file_name,file_name)
        self.assertEqual(file_vertext.source,location)


    def test_create_block_content_node(self):
       self._test_create_block_content_node(create_block_content_node)


    def _test_create_block_content_node(self, creator: Callable[[dict[str, Any]], RoamVertex]):
        content: str = "> Write a program that prints out the numbers 1 to 100 (inclusive). If the number is evenly divisible by 3, print __'Fizz'__ instead of the number. If the number is evenly divisible by 5, print __'Buzz'__ instead of the number. If the number is evenly divisible by both 3 and 5, print __'FizzBuzz'__ instead of the number.\n\nThe output should look exactly like this: 1,2,Fizz,4,Buzz,Fizz,7,8,Fizz,Buzz,11,Fizz,13,14,FizzBuzz,16,17,Fizz,19,Buzz,Fizz,22,23,Fizz,Buzz,26,Fizz,28,29,FizzBuzz,31,32,Fizz,34,Buzz,Fizz,37,38,Fizz,Buzz,41,Fizz,43,44,FizzBuzz,46,47,Fizz,49,Buzz,Fizz,52,53,Fizz,Buzz,56,Fizz,58,59,FizzBuzz,61,62,Fizz,64,Buzz,Fizz,67,68,Fizz,Buzz,71,Fizz,73,74,FizzBuzz,76,77,Fizz,79,Buzz,Fizz,82,83,Fizz,Buzz,86,Fizz,88,89,FizzBuzz,91,92,Fizz,94,Buzz,Fizz,97,98,Fizz,Buzz"
        children: list[Uid] = [
            "a9PURgUrs",
            "GI38yM-z4"        
        ]
        refs: list[Uid] = [
            "o2hTH3dbf",
            "YMkrw0y7Y"      
        ]
        uid: Uid = "Mw66e2LRj"
        vertex_type: VertexType = VertexType.ROAM_BLOCK_CONTENT
        vertex_type_value: str = vertex_type.value
        media_type: MediaType = MediaType.TEXT_PLAIN
        media_type_value: str = media_type.value
        source: dict = {
            "text": content,
            "children": children,
            "refs": refs,
            "uid": uid,
            "vertex-type": vertex_type_value,
            "media-type": media_type_value
        }
        logging.debug(f"source: {source}")
        block_content_node: BlockContentNode = cast(BlockContentNode, creator(source))
        logging.debug(f"block_content_node: {block_content_node}")
        self.assertEqual(block_content_node.uid,uid)
        self.assertEqual(block_content_node.vertex_type,vertex_type)
        self.assertEqual(block_content_node.media_type,media_type)
        self.assertEqual(block_content_node.content,content)
        self.assertEqual(block_content_node.children,children)
        self.assertEqual(block_content_node.references,refs)


    def test_create_block_heading_node(self):
       self._test_create_block_heading_node(create_block_heading_node)


    def _test_create_block_heading_node(self, creator: Callable[[dict[str, Any]], RoamVertex]):
        heading: str = "solution 2 (hard to understand)"
        level: int = 1
        children: list[Uid] = [
            "Gi1BCIGoW"
        ]
        uid: Uid = "4jf3ZlLqF"
        vertex_type: VertexType = VertexType.ROAM_BLOCK_HEADING
        vertex_type_value: str = vertex_type.value
        media_type: MediaType = MediaType.TEXT_PLAIN
        media_type_value: str = media_type.value
        source: dict = {
            "heading": heading,
            "level": level,
            "children": children,
            "uid": uid,
            "vertex-type": vertex_type_value,
            "media-type": media_type_value
        }
        logging.debug(f"source: {source}")
        block_heading_node: BlockHeadingNode = cast(BlockHeadingNode, creator(source))
        logging.debug(f"block_heading_node: {block_heading_node}")
        self.assertEqual(block_heading_node.uid,uid)
        self.assertEqual(block_heading_node.vertex_type,vertex_type)
        self.assertEqual(block_heading_node.media_type,media_type)
        self.assertEqual(block_heading_node.heading,heading)
        self.assertEqual(block_heading_node.level,level)
        self.assertEqual(block_heading_node.children,children)
        self.assertEqual(block_heading_node.references,None)


    def test_create_page_node(self):
       self._test_create_page_node(create_page_node)


    def _test_create_page_node(self, creator: Callable[[dict[str, Any]], RoamVertex]):
        text: str = "Page 3"
        children: list[Uid] = [
            "IO75SriD8",
            "uFL-CFN6i",
            "LXoC6aV1-",
            "dftwwQg-V"
        ]
        uid: Uid = "hfm6NKq2c"
        vertex_type: VertexType = VertexType.ROAM_PAGE
        vertex_type_value: str = vertex_type.value
        media_type: MediaType = MediaType.TEXT_PLAIN
        media_type_value: str = media_type.value
        source: dict = {
            "text": text,
            "children": children,
            "uid": uid,
            "vertex-type": vertex_type_value,
            "media-type": media_type_value
        }
        logging.debug(f"source: {source}")
        page_node: PageNode = cast(PageNode, creator(source))
        logging.debug(f"page_node: {page_node}")
        self.assertEqual(page_node.uid,uid)
        self.assertEqual(page_node.vertex_type,vertex_type)
        self.assertEqual(page_node.media_type,media_type)
        self.assertEqual(page_node.title,text)
        self.assertEqual(page_node.children,children)
        self.assertEqual(page_node.references,None)

        source["vertex-type"] = VertexType.ROAM_BLOCK_CONTENT.value
        with self.assertRaises(ValueError):
            page_node: PageNode = create_page_node(source)


    def test_enum_lookup(self):
        found: VertexType = VertexType('roam/page')
        logging.debug(f"found: {found}")


    def setUp(self):
        configure_logging()
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()