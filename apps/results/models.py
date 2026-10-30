from decimal import Decimal

from django.db import models


class Exam(models.Model):
    """An assessment event for a subject within a section."""

    EXAM_TYPE_CHOICES = [
        ('midterm', 'Midterm'),
        ('final', 'Final'),
        ('practical', 'Practical'),
    ]

    name = models.CharField(max_length=100)
    exam_type = models.CharField(
        max_length=15, choices=EXAM_TYPE_CHOICES, default='final'
    )
    subject = models.ForeignKey(
        'academics.Subject', on_delete=models.CASCADE, related_name='exams'
    )
    section = models.ForeignKey(
        'academics.Section', on_delete=models.CASCADE, related_name='exams'
    )
    date = models.DateField()
    total_marks = models.PositiveSmallIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Unique exam identity and newest-first ordering."""

        unique_together = [('subject', 'section', 'exam_type', 'name')]
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} - {self.subject.code} ({self.section})"


class Mark(models.Model):
    """A student's score for a single exam."""

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='marks')
    student = models.ForeignKey(
        'accounts.StudentProfile', on_delete=models.CASCADE, related_name='marks'
    )
    marks_obtained = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    is_absent = models.BooleanField(default=False)

    class Meta:
        """One mark per student per exam, ordered by roll number."""

        unique_together = [('exam', 'student')]
        ordering = ['student__roll_no']

    def __str__(self):
        return (
            f"{self.student.roll_no} - {self.exam} - "
            f"{self.marks_obtained}/{self.exam.total_marks}"
        )
