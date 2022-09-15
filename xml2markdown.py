import xml.dom.minidom as md
from datetime import datetime
from pathlib import Path
from string import Template

import unidecode

VERSION = "NVI"
OUTPUT = VERSION

BIBLE_MOC_TEMPLATE = "bible_moc_template.md"
CHAPTER_MOC_TEMPLATE = "book_moc_template.md"
CHAPTER_TEMPLATE = "chapter_template.md"


def remove_accent(text):
    return unidecode.unidecode(text)


def render_template(template_name, context):
    template_file = open(template_name, "r")
    content = template_file.read()

    return Template(str(content)).substitute(**context)


def get_or_create_book_folder(book):
    directory: Path = Path(OUTPUT) / book
    directory.mkdir(parents=True, exist_ok=True)

    return directory


def bible_moc_md(books):
    bible_moc_file = Path(OUTPUT) / "Biblia-NVI.md"
    created = datetime.now().strftime("%Y-%m-%d")

    books_md = []
    for book in books:
        name = book.getAttribute("name")
        books_md.append(f"- [[{remove_accent(name)}|{name}]]")

    with bible_moc_file.open("a", encoding="utf-8") as bible_moc_content:
        content = render_template(
            BIBLE_MOC_TEMPLATE,
            {
                "books": "\n".join(books_md),
                "created": created,
            },
        )
        bible_moc_content.writelines(content)


def create_book_moc_md(num, book, chapters):
    book_name = f"{num} - {book}"
    book_path = get_or_create_book_folder(book_name)
    created = datetime.now().strftime("%Y-%m-%d")

    moc_file = book_path / f"{book}.md"

    chapters_filenames = []
    for chapter in chapters:
        number = chapter.getAttribute("n")
        titulo = f"- [[{book} {number}|{book} {number}]]"
        chapters_filenames.append(titulo)

    with moc_file.open("a", encoding="utf-8") as moc_content:
        content = render_template(
            CHAPTER_MOC_TEMPLATE,
            {
                "book": book,
                "created": created,
                "chapters": "\n".join(chapters_filenames),
            },
        )
        moc_content.writelines(content)


def write2File(num, book, versicules, nomeDoArquivo):
    book_name = f"{num} - {book}"
    book_path = get_or_create_book_folder(book_name)

    chapter_file = book_path / f"{nomeDoArquivo}.md"

    with chapter_file.open("a", encoding="utf-8") as f:

        versicules_md = []
        for versicule in versicules:
            number = versicule.getAttribute("n")
            versicules_md.append(
                f"###### v{number}\n" f"{versicule.firstChild.nodeValue}\n"
            )

        created = datetime.now().strftime("%Y-%m-%d")
        content = render_template(
            CHAPTER_TEMPLATE,
            {
                "book": book,
                "shortbook": book[:3],
                "created": created,
                "number": num,
                "versicules": "".join(versicules_md),
            },
        )
        f.writelines(content)


def main():
    directory: Path = Path(OUTPUT)
    directory.mkdir(parents=True, exist_ok=True)

    file = md.parse(VERSION + ".xml")
    books = file.getElementsByTagName("book")

    bible_moc_md(books)

    for num, book in enumerate(books, 1):
        name = book.getAttribute("name")
        chapters = book.getElementsByTagName("c")

        name = remove_accent(name)
        create_book_moc_md(num, name, chapters)

        for chapter in chapters:
            chapter_number = chapter.getAttribute("n")
            versicules = chapter.getElementsByTagName("v")

            titulo = f"{name} {chapter_number}"
            write2File(num, name, versicules, titulo)


if __name__ == "__main__":
    main()
