import pytest
from app.models import ShortenedLink
from app import db

class TestShortenedLink:

    def test_create_shortened_link(self, db):
        link = ShortenedLink(
            original_link='https://example.com/test',
            short_link='example1'
        )
        db.session.add(link)
        db.session.commit()
        
        saved_link = ShortenedLink.query.first()
        assert saved_link is not None
        assert saved_link.original_link == 'https://example.com/test'
        assert saved_link.short_link == 'example1'
        assert saved_link.number_of_redirections == 0

    def test_to_dict_method(self, db, sample_link):
        link_dict = sample_link.to_dict()
        
        assert isinstance(link_dict, dict)
        assert link_dict['id'] == sample_link.id
        assert link_dict['original_link'] == sample_link.original_link
        assert link_dict['short_link'] == sample_link.short_link
        assert link_dict['number_of_redirections'] == sample_link.number_of_redirections

    def test_repr_method(self, db, sample_link):
        repr_str = repr(sample_link)

        assert 'ShortenedLink' in repr_str
        assert sample_link.original_link in repr_str
        assert sample_link.short_link in repr_str

    def test_unique_short_link_constraint(self, db):
        link1 = ShortenedLink(
            original_link='https://example1.com',
            short_link='unique12'
        )
        db.session.add(link1)
        db.session.commit()
        
        link2 = ShortenedLink(
            original_link='https://example2.com',
            short_link='unique12'
        )
        db.session.add(link2)
        
        with pytest.raises(Exception):  # IntegrityError
            db.session.commit()
        db.session.rollback()