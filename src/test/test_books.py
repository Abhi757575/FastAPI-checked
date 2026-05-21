from src.test.conftest import fake_session


books_prefix = f"api/v1/books"

def test_Get_all_books(test_client, fake_book_Service):
    response = test_client.get(
        url=f"{books_prefix}"
    )

    assert fake_book_Service.get_all_books_called_once()    
    assert fake_book_Service.get_all_books_called_once_with(fake_session)
