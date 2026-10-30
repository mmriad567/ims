from decimal import Decimal

from .models import Exam, Mark

GRADE_TABLE = [
    (80, 'A+', Decimal('4.00')),
    (75, 'A', Decimal('3.75')),
    (70, 'A-', Decimal('3.50')),
    (65, 'B+', Decimal('3.25')),
    (60, 'B', Decimal('3.00')),
    (55, 'B-', Decimal('2.75')),
    (50, 'C+', Decimal('2.50')),
    (45, 'C', Decimal('2.25')),
    (40, 'D', Decimal('2.00')),
    (0, 'F', Decimal('0.00')),
]


def marks_to_grade(percentage):
    """Convert a percentage (0-100) to (grade_letter, grade_point) using BTEB scale."""
    for min_pct, letter, point in GRADE_TABLE:
        if percentage >= min_pct:
            return letter, point
    return 'F', Decimal('0.00')


def calculate_exam_result(exam, student):
    """Return dict with obtained/total/percentage/grade/grade_point for one exam."""
    try:
        mark = Mark.objects.get(exam=exam, student=student)
    except Mark.DoesNotExist:
        return None
    if mark.is_absent:
        return {
            'exam': exam,
            'obtained': Decimal('0'),
            'total': exam.total_marks,
            'percentage': 0.0,
            'grade': 'F',
            'grade_point': Decimal('0.00'),
            'is_absent': True,
        }
    percentage = round(float(mark.marks_obtained) / exam.total_marks * 100, 2)
    letter, point = marks_to_grade(percentage)
    return {
        'exam': exam,
        'obtained': mark.marks_obtained,
        'total': exam.total_marks,
        'percentage': percentage,
        'grade': letter,
        'grade_point': point,
        'is_absent': False,
    }


def calculate_subject_gpa(student, subject):
    """Average the grade points of all exams in a subject for a student."""
    exams = Exam.objects.filter(subject=subject, section=student.section)
    results = [calculate_exam_result(e, student) for e in exams]
    results = [r for r in results if r is not None]
    if not results:
        return {'subject': subject, 'exams': [], 'gpa': None, 'has_fail': False}
    has_fail = any(r['grade'] == 'F' for r in results)
    gpa = Decimal('0.00') if has_fail else (
        sum(r['grade_point'] for r in results) / len(results)
    )
    return {
        'subject': subject,
        'exams': results,
        'gpa': round(gpa, 2),
        'has_fail': has_fail,
    }


def calculate_overall_result(student):
    """Compute overall GPA across all subjects in the student's semester."""
    from apps.academics.models import Subject

    subjects = Subject.objects.filter(
        semester=student.section.semester
    ).order_by('code')
    subject_results = [calculate_subject_gpa(student, s) for s in subjects]
    graded = [r for r in subject_results if r['gpa'] is not None]
    if not graded:
        return {
            'subjects': subject_results,
            'overall_gpa': None,
            'has_fail': False,
        }
    has_fail = any(r['has_fail'] for r in graded)
    if has_fail:
        overall = Decimal('0.00')
    else:
        total_points = sum(r['gpa'] for r in graded)
        overall = round(total_points / len(graded), 2)
    return {
        'subjects': subject_results,
        'overall_gpa': overall,
        'has_fail': has_fail,
    }
