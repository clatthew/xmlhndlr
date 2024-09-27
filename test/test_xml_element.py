from pytest import mark, fixture, raises
from src.xml_element import XMLElement
from pickle import load
from book_store.book_store import build_bookstore_file
import os


@fixture(scope="function")
def root_element():
    return XMLElement("bookstore", is_root=True)


class Test__init__:
    @mark.it(
        "XMLElement is initialised with tag, attribute, value, root, children, parent and root by default"
    )
    def test_default_vals(self, root_element):
        assert "tag" in dir(root_element)
        assert "attribute" in dir(root_element)
        assert "value" in dir(root_element)
        assert "is_root" in dir(root_element)
        assert "children" in dir(root_element)
        assert "parent" in dir(root_element)
        assert "root" in dir(root_element)

    @mark.it("Root element root value is self")
    def test_root_element_root(self, root_element):
        assert root_element.root is root_element


class Testadd_child:
    @mark.it("Added child has the correct parent")
    def test_correct_parent(self, root_element):
        test_child = XMLElement("book")
        root_element.add_child(test_child)
        assert root_element.last_child.parent is root_element

    @mark.it("Added child's is_root is false")
    def test_correct_root(self, root_element):
        test_child = XMLElement("book", is_root=True)
        root_element.add_child(test_child)
        assert not root_element.last_child.is_root

    @mark.it("Raises ValueError if calling add_child on self")
    def test_index_error_self_add(self, root_element):
        with raises(ValueError) as err:
            root_element.add_child(root_element)
        assert str(err.value) == "cannot add descendant as child"

    @mark.it("Added child's descendants' roots match its parent's")
    def test_correct_root_deep(self, root_element):
        test_parent = XMLElement("book", is_root=True)
        test_child = XMLElement("title")
        test_parent.add_child(test_child)
        root_element.add_child(test_parent)
        assert root_element.last_child.root is root_element
        assert root_element.last_child.last_child.root is root_element


class Testpath:
    @mark.it("Root element has path []")
    def test_root_path(self, root_element):
        assert root_element.path == []

    @mark.it("First child added to root element has path [0]")
    def test_first_child_path(self, root_element):
        test_child = XMLElement("book")
        root_element.add_child(test_child)
        assert test_child.path == [0]

    @mark.it(
        "Third child added to first child added to root element has path [0, 2]. Path is correct, irrelevant of what order elements were added."
    )
    def test_first_child_third_child_path(self, root_element):
        test_child1 = XMLElement("book", is_root=True)
        test_child2 = XMLElement("title")
        test_child3 = XMLElement("length")
        test_child4 = XMLElement("price")
        test_child1.add_child(test_child2)
        test_child1.add_child(test_child3)
        test_child1.add_child(test_child4)
        root_element.add_child(test_child1)
        assert test_child4.path == [0, 2]

    @mark.it("That child's second child has path [0, 2, 1]")
    def test_first_child_third_child_child_path(self, root_element):
        test_child1 = XMLElement("book", is_root=True)
        test_child2 = XMLElement("title")
        test_child3 = XMLElement("length")
        test_child4 = XMLElement("price")
        root_element.add_child(test_child1)
        root_element.last_child.add_child(test_child2)
        root_element.last_child.add_child(test_child3)
        root_element.last_child.add_child(test_child4)
        test_child4.make_child("euro", value=20)
        test_child4.make_child("pound", value=18)
        assert test_child4.last_child.path == [0, 2, 1]


class Testmake_child:
    @mark.it("make_child adds an instance of XMLElement to children")
    def test_add_child_instance(self, root_element):
        root_element.make_child("book")
        for child in root_element.children:
            assert isinstance(child, XMLElement)

    @mark.it("make_child sets correct attribute")
    def test_add_child_attribute(self, root_element):
        root_element.make_child("book", ("category", "cooking"))
        assert root_element.children[0].attribute == ("category", "cooking")

    @mark.it("make_child sets correct value")
    def test_add_child_value(self, root_element):
        root_element.make_child("book", value="Matthew")
        assert root_element.children[0].value == "Matthew"


class Testadd_sibling:
    @mark.it("add_sibling adds an instance of XMLElement to parent's children")
    def test_add_sibline(self, root_element):
        root_element.make_child("book")
        root_element.children[0].make_sibling(value="Carrots")
        assert len(root_element.children) == 2
        assert root_element.children[1].value == "Carrots"

    @mark.it("add_sibling sets new sibling's tag to own value by default")
    def test_add_subling_tag(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_sibling()
        for child in root_element.children:
            assert child.tag == "book"


class Testlast_child:
    @mark.it("last_child returns only child")
    def test_last_child_one_child(self, root_element):
        test_child = XMLElement("book")
        root_element.add_child(test_child)
        assert root_element.last_child is test_child

    @mark.it("last_child returns None if children is empty")
    def test_last_child_no_child(self, root_element):
        assert not root_element.last_child

    @mark.it("last_child returns last child of many")
    def test_last_child_one_child(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("book")
        test_child3 = XMLElement("book")
        root_element.add_child(test_child1)
        root_element.add_child(test_child2)
        root_element.add_child(test_child3)
        assert root_element.last_child is test_child3


class Testdepth:
    @mark.it("root element returns depth 0")
    def test_depth_0(self, root_element):
        result = root_element.depth
        assert result == 0

    @mark.it("child of root element returns depth 1")
    def test_depth_1(self, root_element):
        root_element.make_child("book")
        result = root_element.last_child.depth
        assert result == 1

    @mark.it("grandchild of root element returns depth 2")
    def test_depth_2(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_child("title")
        result = root_element.last_child.last_child.depth
        assert result == 2

    @mark.it("great grandchild of root element returns depth 3")
    def test_depth_3(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_child("title")
        root_element.last_child.last_child.make_child("colour")
        result = root_element.last_child.last_child.last_child.depth
        assert result == 3


class Testno_children:
    @mark.it("Element with no children added has 0 children")
    def test_no_children(self, root_element):
        assert root_element.no_children == 0

    @mark.it("Correctly returns number of direct children of an element")
    def test_many_children(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_sibling()
        root_element.last_child.make_child("title")
        assert root_element.no_children == 2


class Testsize:
    @mark.it("Element with nothing added has size 1")
    def test_size(self, root_element):
        assert root_element.size == 1

    @mark.it("Returns size of element whose children are all 'leaves'")
    def test_no_deep_descendants(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_sibling()
        assert root_element.size == 3

    @mark.it("Correcrtly returns size of nested tree")
    def test_deep_size(self):
        with open("book_store/bookstore.pkl", "rb") as f:
            loaded_tree = load(f)
        assert loaded_tree.size == 16


# This should be made into a true interator
class Test__iter__:
    @mark.it("Root element's descendants are only itself")
    def test_root_descendants(self, root_element):
        assert len(root_element.descendants) == 1
        for descendant in list(root_element):
            assert descendant is root_element

    @mark.it(
        "Correctly returns descendants for element whose children are all 'leaves'"
    )
    def test_root_1_gen(self, root_element):
        root_element.make_child("book")
        root_element.last_child.make_sibling()
        root_element.last_child.make_sibling()
        root_element.last_child.make_sibling()
        expected = [root_element] + root_element.children
        result = list(root_element)
        assert result == expected

    @mark.it("Correctly returns descendants for deep tree")
    def test_deep_descendants(self, root_element):
        test_child1 = XMLElement("book")
        root_element.add_child(test_child1)
        test_child11 = XMLElement("title", value="Harry Potter")
        root_element.last_child.add_child(test_child11)
        test_child2 = XMLElement("book")
        root_element.add_child(test_child2)
        test_child21 = XMLElement("title", value="Normal People")
        root_element.last_child.add_child(test_child21)
        test_child3 = XMLElement("book")
        root_element.add_child(test_child3)
        test_child31 = XMLElement("title", value="To Kill a Mockingbird")
        root_element.last_child.add_child(test_child31)
        test_child32 = XMLElement("price", value=9.99)
        root_element.last_child.add_child(test_child32)
        assert root_element.size == 8
        descendants = list(root_element)
        for xmlelt in [
            test_child1,
            test_child2,
            test_child3,
            test_child11,
            test_child21,
            test_child31,
            test_child32,
            root_element,
        ]:
            assert xmlelt in descendants


class Test_make_xml_tags:
    @mark.it("Root element has correct XML tags")
    def test_root_tags(self, root_element):
        tag = root_element.tag
        expected = ["", f"<{tag}>", None, f"</{tag}>"]
        assert root_element.make_xml_tags() == expected

    @mark.it("Element with attribute has correct XML tags")
    def test_attribute_tags(self, root_element):
        test_parent = XMLElement(
            "book", attribute=("category", "children"), is_root=True
        )
        root_element.add_child(test_parent)
        tag = root_element.last_child.tag
        expected = ["  ", f'<{tag} category="children">', None, f"</{tag}>"]
        assert root_element.last_child.make_xml_tags() == expected

    @mark.it("Leaf element with value has correct XML tags")
    def test_value_tags(self, root_element):
        tag = root_element.tag
        test_parent = XMLElement(
            "book", attribute=("category", "children"), is_root=True
        )
        test_child = XMLElement("title", value="Harry Potter")
        test_parent.add_child(test_child)
        root_element.add_child(test_parent)
        tag = root_element.last_child.last_child.tag
        expected = ["    ", f"<{tag}>", "Harry Potter", f"</{tag}>"]
        assert root_element.last_child.last_child.make_xml_tags() == expected

    @mark.it("Leaf element with value and attribute has correct XML tags")
    def test_value_attribute_tags(self, root_element):
        tag = root_element.tag
        test_parent = XMLElement(
            "book", attribute=("category", "children"), is_root=True
        )
        test_child = XMLElement(
            "title", attribute=("quality", "terrible"), value="Harry Potter"
        )
        test_parent.add_child(test_child)
        root_element.add_child(test_parent)
        tag = root_element.last_child.last_child.tag
        expected = ["    ", f'<{tag} quality="terrible">', "Harry Potter", f"</{tag}>"]
        assert root_element.last_child.last_child.make_xml_tags() == expected

    @mark.it("Leaf element with numerical value has correct XML tags")
    def test_value_tags_int(self, root_element):
        tag = root_element.tag
        test_parent = XMLElement(
            "book", attribute=("category", "children"), is_root=True
        )
        test_child = XMLElement("price", value=555)
        test_parent.add_child(test_child)
        root_element.add_child(test_parent)
        tag = root_element.last_child.last_child.tag
        expected = ["    ", f"<{tag}>", "555", f"</{tag}>"]
        assert root_element.last_child.last_child.make_xml_tags() == expected


class Testto_xml:
    @mark.it("Forms the correct XML file for the bookstore data")
    def test_correct_xml_output(self):
        # generate pkl file of the bookstore based on bookstore.xml
        build_bookstore_file("pkl")
        # load the pkl file
        with open("book_store/bookstore.pkl", "rb") as f:
            test_tree = load(f)
        # send the object stored in the pkl file to xml using to_xml
        test_tree.to_xml("book_store/test_xml.xml")
        # read the resulting xml file
        with open("book_store/test_xml.xml") as f:
            test_data = f.readlines()
        # read the original xml
        with open("book_store/bookstore.xml") as f:
            bookstore_data = f.readlines()
        # delete the created files
        os.remove("book_store/test_xml.xml")
        # compare the generated xml to the original
        assert bookstore_data == test_data


class Testget_from_path:
    @mark.it("Retrieves root element when passed path []")
    def test_root(self, root_element):
        result = root_element.get_from_path([])
        assert result is root_element

    @mark.it("Retrieves root element's second child when passed path [1]")
    def test_child(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("book")
        root_element.add_child(test_child1)
        root_element.add_child(test_child2)
        result = root_element.get_from_path([1])
        assert result is test_child2

    @mark.it(
        "Retrieves the third child added to first child added to root element when passed path [0, 2]."
    )
    def test_grandchild(self, root_element):
        test_child1 = XMLElement("book", is_root=True)
        test_child2 = XMLElement("title")
        test_child3 = XMLElement("length")
        test_child4 = XMLElement("price")
        test_child1.add_child(test_child2)
        test_child1.add_child(test_child3)
        test_child1.add_child(test_child4)
        root_element.add_child(test_child1)
        result = root_element.get_from_path([0, 2])
        assert result is test_child4

    @mark.it("Retrieves that child's second child when passed path [0, 2, 1]")
    def test_first_child_third_child_child_path(self, root_element):
        test_child1 = XMLElement("book", is_root=True)
        test_child2 = XMLElement("title")
        test_child3 = XMLElement("length")
        test_child4 = XMLElement("price")
        root_element.add_child(test_child1)
        root_element.last_child.add_child(test_child2)
        root_element.last_child.add_child(test_child3)
        root_element.last_child.add_child(test_child4)
        test_child4.make_child("euro", value=20)
        test_child4.make_child("pound", value=18)
        result = root_element.get_from_path([0, 2, 1])
        assert result is test_child4.last_child

    @mark.it("Raises IndexError if requested path is not in the tree")
    def test_index_error(self, root_element):
        with raises(IndexError) as err:
            root_element.get_from_path([0])
        assert str(err.value) == "no element found at path [0]"
        root_element.make_child("book")
        with raises(IndexError) as err:
            root_element.get_from_path([0, 0])
        assert str(err.value) == "no element found at path [0, 0]"


class Testremove_from_path:
    @mark.it("Does not allow removal of the root element")
    def test_remove_root(self, root_element):
        with raises(IndexError) as err:
            root_element.remove_from_path([])
        assert str(err.value) == "cannot remove root element"

    @mark.it(
        "Raises IndexError when attempting to remove element from path not in tree"
    )
    def test_remove_non_existent(self, root_element):
        with raises(IndexError) as err:
            root_element.remove_from_path([0])
        assert str(err.value) == "no element found at path [0]"

    @mark.it("Successfully removes 'leaf' element and updates size accordingly")
    def test_remove_leaf(self, root_element):
        test_child1 = XMLElement("book")
        test_child2 = XMLElement("book")
        root_element.add_child(test_child1)
        root_element.add_child(test_child2)
        root_element.remove_from_path([1])
        assert root_element.size == 2
        assert test_child2 not in list(root_element)

    @mark.it("Successfully removes element with children and updates size accordingly")
    def test_remove_element_with_kids(self, root_element):
        test_child1 = XMLElement("book", is_root=True)
        test_child2 = XMLElement("title")
        test_child3 = XMLElement("length")
        test_child4 = XMLElement("price")
        root_element.add_child(test_child1)
        root_element.last_child.add_child(test_child2)
        root_element.last_child.add_child(test_child3)
        root_element.last_child.add_child(test_child4)
        test_child4.make_child("euro", value=20)
        test_child5 = XMLElement("pound", value=18)
        test_child4.add_child(test_child5)
        root_element.remove_from_path([0, 2])
        assert root_element.size == 4
        assert test_child4 not in list(root_element)
        assert test_child5 not in list(root_element)
