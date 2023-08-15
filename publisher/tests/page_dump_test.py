from typing import Callable, cast
import logging
import unittest
from zipfile import BadZipFile

from common.log import configure_logging
from common.collect import get_first_value, get_last_value

from roampub.roam_model import *
from roampub.page_dump import *

class PageDumpTests(unittest.TestCase):

    def test_get_items(self):
        path: Path = Path('./tests/data/Creative Brief.zip')
        brief_dump: PageDump = PageDump(path)
        items: VertexMap = brief_dump.get_items([])
        self.assertEqual(len(items), 0)

        uids: list[Uid] = ['lALsKb-Dx']
        items: VertexMap = brief_dump.get_items(uids)
        logging.info(f"items: {items}")
        self.assertEqual(len(items), 1)
        self.assertIs(items[uids[0]], brief_dump.root_page)

        uids: list[Uid] = ['lALsKb-Dx', 'C2uKKD4-b']
        items: VertexMap = brief_dump.get_items(uids)
        logging.info(f"items: {items}")
        self.assertEqual(len(items), 2)
        self.assertIs(items[uids[0]], brief_dump.root_page)
        self.assertEqual(items[uids[1]].uid, uids[1])        

        uids: list[Uid] = ['lALsKb-Dx', 'C2uKKD4-b', 'ZdZlJbgy1', '6TCv5eKPQ', '2bW3xKCMS', '4jf3ZlLqF']
        items: VertexMap = brief_dump.get_items(uids)
        self.assertEqual(len(items), 6)

        uids: list[Uid] = ['lALsKb-Dx', 'C2uKKD4-b', 'xxxxxx', '6TCv5eKPQ', '2bW3xKCMS', '4jf3ZlLqF']
        with self.assertRaises(KeyError):
            items: VertexMap = brief_dump.get_items(uids)


    def test_subscript(self):
        path: Path = Path('./tests/data/Creative Brief.zip')
        brief_dump: PageDump = PageDump(path)
        uid: Uid = 'lALsKb-Dx'
        root_page: PageNode = brief_dump[uid] # type: ignore
        logging.info(f"root_page: {root_page}")
        self.assertIsNotNone(root_page)
        self.assertEqual(root_page.uid, uid)
        self.assertIsInstance(root_page, PageNode)
        self.assertIs(root_page.vertex_type, VertexType.ROAM_PAGE)
        self.assertEqual(root_page.title, 'Creative Brief')

        uid: Uid = 'ZnUfgOM7W'
        node: RoamNode = brief_dump[uid] # type: ignore
        logging.info(f"node: {node}")
        self.assertIsNotNone(node)
        self.assertEqual(node.uid, uid)
        self.assertIsInstance(node, BlockContentNode)

        with self.assertRaises(KeyError):
            node: RoamNode = brief_dump['hfm6NKq2c'] # type: ignore

        path: Path = Path('./tests/data/Page 3.zip')
        page3_dump: PageDump = PageDump(path)
        uid: Uid = 'hfm6NKq2c'
        root_page: PageNode = page3_dump[uid] # type: ignore
        logging.info(f"root_page: {root_page}")
        self.assertIsNotNone(root_page)
        self.assertEqual(root_page.uid, uid)
        self.assertIsInstance(root_page, PageNode)
        self.assertIs(root_page.vertex_type, VertexType.ROAM_PAGE)
        self.assertEqual(root_page.title, 'Page 3')


    def test_len(self):
        path: Path = Path('./tests/data/Creative Brief.zip')
        brief_dump: PageDump = PageDump(path)
        self.assertEqual(len(brief_dump), 12)

        path: Path = Path('./tests/data/Page 3.zip')
        page3_dump: PageDump = PageDump(path)
        self.assertEqual(len(page3_dump), 30)


    def test_root_page(self):
        path: Path = Path('./tests/data/Creative Brief.zip')
        logging.debug(f"path: {path}")
        brief_dump: PageDump = PageDump(path)
        logging.debug(f"brief_dump: {brief_dump}")
        self.assertEqual(brief_dump.root_page, brief_dump.vertex_map['lALsKb-Dx'])

        path: Path = Path('./tests/data/Page 3.zip')
        page3_dump: PageDump = PageDump(path)
        logging.debug(f"page3_dump: {page3_dump}")
        self.assertEqual(page3_dump.root_page, page3_dump.vertex_map['hfm6NKq2c'])
       

    def test_page_dump_class(self):
        path: Path = Path('./tests/data/Creative Brief.zip')
        logging.debug(f"path: {path}")
        brief_dump: PageDump = PageDump(path)
        logging.debug(f"brief_dump: {brief_dump}")
        self.assertEqual(path, brief_dump.zip_path)

        brief_vertex_map: VertexMap = brief_dump.vertex_map
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self._validate_brief_map(brief_vertex_map)

        path: Path = Path('./tests/data/Page 3.zip')
        page3_dump: PageDump = PageDump(path)
        logging.debug(f"page3_dump: {page3_dump}")
        page3_vertex_map: VertexMap = page3_dump.vertex_map
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self._validate_page3_map(page3_vertex_map)


    def test_page_dump_invalid_files(self):
        path: Path = Path('./tests/data/Creative Brief.json')
        with self.assertRaises(BadZipFile):
            page_dump: PageDump = PageDump(path)


        path: Path = Path('./tests/data/Creative Brief.xxxxxx')
        with self.assertRaises(FileNotFoundError):
            page_dump: PageDump = PageDump(path)


    def test_create_vertex_map(self):
        page3_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Page 3.json'))
        logging.debug(f"page3_vertex_map: {page3_vertex_map}")
        self._validate_page3_map(page3_vertex_map)
    
        brief_vertex_map: VertexMap = load_json_dump(Path('./tests/data/Creative Brief.json'))
        logging.debug(f"brief_vertex_map: {brief_vertex_map}")
        self._validate_brief_map(brief_vertex_map)


    def _validate_page3_map(self, vertex_map: VertexMap) -> None:
        self.assertEqual(len(vertex_map),30)
        self.assertEqual(sum(1 for i in vertex_map.values() if i.vertex_type is VertexType.ROAM_PAGE),4)
        self.assertEqual(sum(1 for i in vertex_map.values() if i.vertex_type is VertexType.ROAM_FILE),2)
        self.assertEqual(sum(1 for i in vertex_map.values() if i.vertex_type is VertexType.ROAM_BLOCK_HEADING),0)
        self.assertEqual(sum(1 for i in vertex_map.values() if i.vertex_type is VertexType.ROAM_BLOCK_CONTENT),24)

        first: PageNode = cast(PageNode,get_first_value(vertex_map))
        logging.debug(f"first: {first}")
        self.assertEqual(first.uid, 'hfm6NKq2c')
        self.assertEqual(first.vertex_type,VertexType.ROAM_PAGE)
        self.assertEqual(first.media_type,MediaType.TEXT_PLAIN)
        self.assertEqual(first.title,'Page 3')
        self.assertEqual(first.children,["IO75SriD8","uFL-CFN6i","LXoC6aV1-","dftwwQg-V"])
        self.assertIsNone(first.references)

        last: BlockContentNode = cast(BlockContentNode, get_last_value(vertex_map))
        logging.debug(f"last: {last}")
        self.assertEqual(last.uid, 'mvVww9zGd')
        self.assertEqual(last.vertex_type,VertexType.ROAM_BLOCK_CONTENT)
        self.assertEqual(last.media_type,MediaType.TEXT_PLAIN)
        self.assertEqual(last.content,'Block 1.2')
        self.assertEqual(last.children,["Wu-bKjjdJ"])
        self.assertIsNone(last.references)


    def _validate_brief_map(self, vertex_map: VertexMap) -> None:
        self.assertEqual(len(vertex_map),12)
        self.assertEqual(sum(1 for i in vertex_map.values() if i.vertex_type is VertexType.ROAM_PAGE),1)
        self.assertEqual(sum(1 for i in vertex_map.values() if i.vertex_type is VertexType.ROAM_FILE),0)
        self.assertEqual(sum(1 for i in vertex_map.values() if i.vertex_type is VertexType.ROAM_BLOCK_HEADING),3)
        self.assertEqual(sum(1 for i in vertex_map.values() if i.vertex_type is VertexType.ROAM_BLOCK_CONTENT),8)

        first: PageNode = cast(PageNode,get_first_value(vertex_map))
        logging.debug(f"first: {first}")
        self.assertEqual(first.uid, 'lALsKb-Dx')
        self.assertEqual(first.vertex_type,VertexType.ROAM_PAGE)
        self.assertEqual(first.media_type,MediaType.TEXT_PLAIN)
        self.assertEqual(first.title,'Creative Brief')
        self.assertEqual(first.children,[
            "C2uKKD4-b",
            "ZdZlJbgy1",
            "6TCv5eKPQ",
            "2bW3xKCMS",
            "4jf3ZlLqF",
            "ZnUfgOM7W",
            "6r7Q5nxw5"
        ])
        self.assertIsNone(first.references)
        
        last: BlockContentNode = cast(BlockContentNode, get_last_value(vertex_map))
        logging.debug(f"last: {last}")
        self.assertEqual(last.uid, '6r7Q5nxw5')
        self.assertEqual(last.vertex_type,VertexType.ROAM_BLOCK_CONTENT)
        self.assertEqual(last.media_type,MediaType.TEXT_PLAIN)
        self.assertEqual(last.content,'So every programmer, whether they know it or not, is making a decision each time they write some code-- ')
        self.assertIsNone(last.children)
        self.assertIsNone(last.references)


    def test_read_page_dump_json(self):
        creative_brief_json: list[dict[str, Any]] = read_page_dump_json(Path('./tests/data/Creative Brief.json'))
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

        page3_json: list[dict[str, Any]] = read_page_dump_json(Path('./tests/data/Page 3.json'))
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


    def _test_create_block_heading_node(self, creator: Callable[[dict[str, Any]], RoamVertex]) -> None:
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
            "text": heading,
            "heading": level,
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
        configure_logging(logging.INFO)
        logging.debug("logging configured")



if __name__ == '__main__':
    unittest.main()