import unittest
from crawl import * #normalize_url, get_heading_from_html, get_first_paragraph_from_html, get_urls_from_html

class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_basic(self):
        input_body = "<html><body><h1>Test Title</h1></body></html>"
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_h2(self):
        input_body = "<html><body><h2>Intro</h2></body></html>"
        actual = get_heading_from_html(input_body)
        expeceted = "Intro"
        self.assertEqual(actual, expeceted)

    def test_get_heading_from_html_no_h(self):
        input_body = "<html><body><p>Hello</p></body></html>"
        actual = get_heading_from_html(input_body)
        self.assertEqual(actual, "")


    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = """<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_first_p(self):
        input_body = """<html><body>
            <p>First paragraph.</p>
            <p>Second paragraph.</p>
            <p>Third paragraph.</p>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "First paragraph."
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_paragraph_outside_main(self):
        input_body = """<html><body>
        <main>
            <h1>Heading.</h1>
        </main>
        <p>First paragraph.</p>
        <p>Second paragraph.</p>
        </body></html>"""
        actual = get_first_paragraph_from_html(input_body)
        expected = "First paragraph."
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_relative_without_slash(self):
        input_url = "https://crawler-test.com"
        input_body = '<a href="page">Page</a>'
        self.assertEqual(
            get_urls_from_html(input_body, input_url),
            ["https://crawler-test.com/page"],
        )

    def test_relative_to_base_with_path(self):
        input_url = "https://crawler-test.com/blog/post"
        input_body = '<a href="other">Other</a>'
        self.assertEqual(
            get_urls_from_html(input_body, input_url),
            ["https://crawler-test.com/blog/other"],
        )

    def test_parent_directory(self):
        input_url = "https://crawler-test.com/a/b/"
        input_body = '<a href="../x">Up</a>'
        self.assertEqual(
            get_urls_from_html(input_body, input_url),
            ["https://crawler-test.com/a/x"],
        )

    def test_protocol_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<a href="//cdn.example.com/file">CDN</a>'
        self.assertEqual(
            get_urls_from_html(input_body, input_url),
            ["https://cdn.example.com/file"],
        )

    def test_query_and_fragment(self):
        input_url = "https://crawler-test.com"
        input_body = '<a href="/search?q=test#results">Search</a>'
        self.assertEqual(
            get_urls_from_html(input_body, input_url),
            ["https://crawler-test.com/search?q=test#results"],
        )

    def test_nested_links(self):
        input_url = "https://crawler-test.com"
        input_body = (
            "<html><body><div><ul>"
            '<li><a href="/deep">Deep</a></li>'
            "</ul></div></body></html>"
        )
        self.assertEqual(
            get_urls_from_html(input_body, input_url),
            ["https://crawler-test.com/deep"],
        )

    def test_duplicates_kept(self):
        input_url = "https://crawler-test.com"
        input_body = '<a href="/same">1</a><a href="/same">2</a>'
        self.assertEqual(
            get_urls_from_html(input_body, input_url),
            ["https://crawler-test.com/same", "https://crawler-test.com/same"],
        )

    def test_empty_href_skipped(self):
        input_url = "https://crawler-test.com"
        input_body = '<a href="">Empty</a><a href="/ok">OK</a>'
        self.assertEqual(
            get_urls_from_html(input_body, input_url),
            ["https://crawler-test.com/ok"],
        )

    def test_non_a_tags_ignored(self):
        input_url = "https://crawler-test.com"
        input_body = (
            '<link href="/style.css">'
            '<img src="/img.png">'
            '<a href="/real">Real</a>'
        )
        self.assertEqual(
            get_urls_from_html(input_body, input_url),
            ["https://crawler-test.com/real"],
        )
    def test_get_images_from_html_relative(self):
            input_url = "https://crawler-test.com"
            input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
            actual = get_images_from_html(input_body, input_url)
            expected = ["https://crawler-test.com/logo.png"]
            self.assertEqual(actual, expected)

    def test_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="https://cdn.example.com/pic.jpg"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://cdn.example.com/pic.jpg"]
        self.assertEqual(actual, expected)

    def test_multiple_images(self):
        input_url = "https://crawler-test.com"
        input_body = (
            "<html><body>"
            '<img src="/one.png">'
            '<img src="https://other.com/two.png">'
            "</body></html>"
        )
        actual = get_images_from_html(input_body, input_url)
        expected = [
            "https://crawler-test.com/one.png",
            "https://other.com/two.png",
        ]
        self.assertEqual(actual, expected)

    def test_missing_src(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img alt="No source"><img src="/ok.png"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/ok.png"]
        self.assertEqual(actual, expected)

    def test_missing_alt_still_included(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/no-alt.png"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/no-alt.png"]
        self.assertEqual(actual, expected)

    def test_empty_src_skipped(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src=""><img src="/ok.png"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/ok.png"]
        self.assertEqual(actual, expected)

    def test_relative_without_slash(self):
        input_url = "https://crawler-test.com/blog/post"
        input_body = '<html><body><img src="images/photo.jpg"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/blog/images/photo.jpg"]
        self.assertEqual(actual, expected)

    def test_nested_image(self):
        input_url = "https://crawler-test.com"
        input_body = (
            "<html><body><div><a href='/page'>"
            '<img src="/nested.png">'
            "</a></div></body></html>"
        )
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/nested.png"]
        self.assertEqual(actual, expected)

    def test_no_images(self):
        input_url = "https://crawler-test.com"
        input_body = "<html><body><p>No images here</p></body></html>"
        actual = get_images_from_html(input_body, input_url)
        expected = []
        self.assertEqual(actual, expected)

    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_h2_fallback_and_main_paragraph(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h2>Subtitle</h2>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Subtitle",
            "first_paragraph": "Main paragraph.",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_multiple_links_and_images(self):
        input_url = "https://crawler-test.com"
        input_body = """<html><body>
            <h1>Gallery</h1>
            <p>Pictures and links.</p>
            <a href="/one">One</a>
            <a href="https://other.com/two">Two</a>
            <a>No href</a>
            <img src="/a.png">
            <img alt="No src">
            <img src="https://cdn.example.com/b.png">
        </body></html>"""
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Gallery",
            "first_paragraph": "Pictures and links.",
            "outgoing_links": [
                "https://crawler-test.com/one",
                "https://other.com/two",
            ],
            "image_urls": [
                "https://crawler-test.com/a.png",
                "https://cdn.example.com/b.png",
            ],
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_empty_page(self):
        input_url = "https://crawler-test.com"
        input_body = "<html><body></body></html>"
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "",
            "first_paragraph": "",
            "outgoing_links": [],
            "image_urls": [],
        }
        self.assertEqual(actual, expected)
if __name__ == "__main__":
    unittest.main()
