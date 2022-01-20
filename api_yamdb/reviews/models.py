from django.db import models
from django.conf import settings

from .validator import validate_year


class Category(models.Model):
    name = models.CharField(unique=True, max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(unique=True, max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Generes'
        ordering = ('id',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField(
        blank=False, null=False, validators=[validate_year])
    description = models.TextField(blank=True, null=True,)
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        through_fields=('title', 'genre'))
    category = models.ForeignKey(
        Category,
        related_name='category',
        on_delete=models.SET_NULL,
        null=True)

    class Meta:
        verbose_name = 'Title'
        verbose_name_plural = 'Titles'
        ordering = ('year',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.SET_NULL,
        null=True)
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True)


class Review(models.Model):
    DEFAULT_CHOICES = (
        (10, '10'),
        (9, '9'),
        (8, '8'),
        (7, '7'),
        (6, '6'),
        (5, '5'),
        (4, '4'),
        (3, '3'),
        (2, '2'),
        (1, '1'),
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        choices=DEFAULT_CHOICES,
        default=0,
        blank=False
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        models.UniqueConstraint(
            fields=['title', 'author'], name='unique_review')
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ('pub_date',)

    def __str__(self):
        return self.author.username


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ('pub_date',)

    def __str__(self):
        return self.text
