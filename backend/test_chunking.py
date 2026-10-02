from database import SessionLocal

from chunking import split_text


sample_text = """
Campus Student Handbook - Test Document

Attendance Requirements

Students are expected to maintain at least 75 percent
attendance in each course. Students with attendance below
the required percentage may be subject to the university's
attendance eligibility rules.

Examination Rules

Students must carry their valid university identification
card to examinations. Electronic devices such as mobile
phones and smart watches are not permitted inside the
examination hall.

Internal Assessment

Internal assessment may include assignments, quizzes,
laboratory work, presentations, and internal examinations.
"""


chunks = split_text(
    sample_text,
    chunk_size=200,
    overlap=50
)


print("\n==============================")
print("CHUNKING TEST")
print("==============================")

print("Total chunks:", len(chunks))

for index, chunk in enumerate(chunks):

    print("\n------------------------------")
    print(f"CHUNK {index}")
    print("------------------------------")

    print(chunk)

    print("\nCharacters:", len(chunk))

print("\n==============================")
print("TEST COMPLETED")
print("==============================")