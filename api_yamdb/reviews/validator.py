import datetime as dt
from rest_framework import serializers


def validate_year(value):
    year = value
    current_year = dt.date.today().year
    if year > current_year:
        raise serializers.ValidationError(
            'Год выпуска не может быть больше текущего!'
        )
    if year < 0:
        raise serializers.ValidationError(
            'Год выпуска не может быть отрицательным числом!'
        )
