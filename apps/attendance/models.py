from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ClassSession(models.Model):
    """A single class period for a subject and section."""

    subject = models.ForeignKey(
        'academics.Subject', on_delete=models.CASCADE, related_name='sessions'
    )
    section = models.ForeignKey(
        'academics.Section', on_delete=models.CASCADE, related_name='sessions'
    )
    teacher = models.ForeignKey(
        'accounts.TeacherProfile', on_delete=models.PROTECT, related_name='sessions'
    )
    date = models.DateField()
    period_no = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('section', 'date', 'period_no')]
        ordering = ['-date', 'period_no']

    def __str__(self):
        return f"{self.subject.code} - {self.section} - {self.date} P{self.period_no}"


class Attendance(models.Model):
    """Attendance status of one student in one class session."""

    STATUS_CHOICES = [('present', 'Present'), ('late', 'Late'), ('absent', 'Absent')]

    session = models.ForeignKey(
        ClassSession, on_delete=models.CASCADE, related_name='attendances'
    )
    student = models.ForeignKey(
        'accounts.StudentProfile', on_delete=models.CASCADE, related_name='attendances'
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    marked_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('session', 'student')]
        ordering = ['student__roll_no']

    def __str__(self):
        return f"{self.student.roll_no} - {self.session} - {self.status}"
