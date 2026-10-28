from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Department(models.Model):
    """Academic department."""

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Semester(models.Model):
    """Semester within a department."""

    number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='semesters'
    )

    class Meta:
        unique_together = [('department', 'number')]
        ordering = ['department__code', 'number']

    def __str__(self):
        return f"{self.department.code} - Semester {self.number}"


class Section(models.Model):
    """Section of a semester for a shift."""

    name = models.CharField(max_length=2, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')])
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name='sections'
    )
    shift = models.CharField(
        max_length=5, choices=[('1st', '1st Shift'), ('2nd', '2nd Shift')]
    )

    class Meta:
        unique_together = [('semester', 'name', 'shift')]
        ordering = ['semester', 'name', 'shift']

    def __str__(self):
        return f"{self.semester} - Section {self.name} ({self.shift})"


class Subject(models.Model):
    """Subject taught in a semester."""

    name = models.CharField(max_length=150)
    code = models.CharField(max_length=10, unique=True)
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name='subjects'
    )
    subject_type = models.CharField(
        max_length=10,
        choices=[('theory', 'Theory'), ('practical', 'Practical')],
        default='theory',
    )

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"
