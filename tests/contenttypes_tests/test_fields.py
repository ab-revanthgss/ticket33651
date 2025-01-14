import json

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.test import TestCase
from django.test.utils import isolate_apps

from .models import Answer, Post, Question


@isolate_apps("contenttypes_tests")
class GenericForeignKeyTests(TestCase):
    def test_str(self):
        class Model(models.Model):
            field = GenericForeignKey()

        self.assertEqual(str(Model.field), "contenttypes_tests.Model.field")

    def test_get_content_type_no_arguments(self):
        with self.assertRaisesMessage(
            Exception, "Impossible arguments to GFK.get_content_type!"
        ):
            Answer.question.get_content_type()

    def test_incorrect_get_prefetch_queryset_arguments(self):
        with self.assertRaisesMessage(
            ValueError, "Custom querysets must be a list for this lookup."
        ):
            Answer.question.get_prefetch_queryset(
                Answer.objects.all(), querysets=Answer.objects.all()
            )

    def test_get_object_cache_respects_deleted_objects(self):
        question = Question.objects.create(text="Who?")
        post = Post.objects.create(title="Answer", parent=question)

        question_pk = question.pk
        Question.objects.all().delete()

        post = Post.objects.get(pk=post.pk)
        with self.assertNumQueries(1):
            self.assertEqual(post.object_id, question_pk)
            self.assertIsNone(post.parent)
            self.assertIsNone(post.parent)


class GenericRelationTests(TestCase):
    def test_value_to_string(self):
        question = Question.objects.create(text="test")
        answer1 = Answer.objects.create(question=question)
        answer2 = Answer.objects.create(question=question)
        result = json.loads(Question.answer_set.field.value_to_string(question))
        self.assertCountEqual(result, [answer1.pk, answer2.pk])
