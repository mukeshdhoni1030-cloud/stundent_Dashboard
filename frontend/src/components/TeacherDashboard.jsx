
import { useEffect, useState } from "react";
import api from "../services/api";

function TeacherDashboard() {
  const [students, setStudents] = useState([]);
  const [exams, setExams] = useState([]);
  const [subjects, setSubjects] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [attendanceDate, setAttendanceDate] = useState(
    new Date().toLocaleDateString("en-CA")
  );
  const [attendanceStatus, setAttendanceStatus] = useState({});
  const [savedAttendance, setSavedAttendance] = useState({});
  const [attendanceLoading, setAttendanceLoading] = useState(false);
  const [attendanceMessage, setAttendanceMessage] = useState("");
  const [attendanceSubmitting, setAttendanceSubmitting] = useState(false);

  const [ownAttendance, setOwnAttendance] = useState([]);
  const [ownAttendanceLoading, setOwnAttendanceLoading] = useState(true);
  const [ownAttendanceError, setOwnAttendanceError] = useState("");

  const [studentId, setStudentId] = useState("");
  const [examId, setExamId] = useState("");
  const [subjectId, setSubjectId] = useState("");
  const [marksObtained, setMarksObtained] = useState("");
  const [maxMarks, setMaxMarks] = useState("");
  const [marksMessage, setMarksMessage] = useState("");
  const [marksSubmitting, setMarksSubmitting] = useState(false);

  // LOAD DASHBOARD DATA
  async function fetchDashboardData() {
    try {
      setLoading(true);
      setError("");

      const [studentResponse, examResponse, subjectResponse] =
        await Promise.all([
          api.get("/teacher/students"),
          api.get("/teacher/exams"),
          api.get("/teacher/subjects"),
        ]);

      setStudents(studentResponse.data);
      setExams(examResponse.data);
      setSubjects(subjectResponse.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Unable to load dashboard information."
      );
    } finally {
      setLoading(false);
    }
  }

  // LOAD TEACHER'S OWN ATTENDANCE HISTORY
  async function fetchMyAttendance() {
    try {
      setOwnAttendanceLoading(true);
      setOwnAttendanceError("");

      const response = await api.get("/teacher/attendance/me");

      setOwnAttendance(response.data);
    } catch (err) {
      setOwnAttendanceError(
        err.response?.data?.detail ||
          "Unable to load your attendance history."
      );
    } finally {
      setOwnAttendanceLoading(false);
    }
  }

  useEffect(() => {
    fetchDashboardData();
    fetchMyAttendance();
  }, []);

  // LOAD SAVED STUDENT ATTENDANCE FOR SELECTED DATE
  async function fetchSavedAttendance(date) {
    if (!date) {
      setSavedAttendance({});
      return;
    }

    try {
      setAttendanceLoading(true);
      setAttendanceMessage("");

      const response = await api.get("/teacher/attendance", {
        params: {
          attendance_date: date,
        },
      });

      const attendanceMap = {};

      response.data.forEach((record) => {
        attendanceMap[record.student_id] = record.status;
      });

      setSavedAttendance(attendanceMap);
    } catch (err) {
      setAttendanceMessage(
        err.response?.data?.detail ||
          "Unable to load saved attendance."
      );
      setSavedAttendance({});
    } finally {
      setAttendanceLoading(false);
    }
  }

  // FETCH STUDENT ATTENDANCE WHEN DATE CHANGES
  useEffect(() => {
    setAttendanceStatus({});
    setSavedAttendance({});
    setAttendanceMessage("");

    fetchSavedAttendance(attendanceDate);
  }, [attendanceDate]);

  // CHANGE STUDENT ATTENDANCE STATUS
  function handleStatusChange(id, status) {
    setAttendanceStatus((previous) => ({
      ...previous,
      [id]: status,
    }));
  }

  // SAVE STUDENT ATTENDANCE
  async function handleSubmitAttendance(id) {
    const status = attendanceStatus[id];

    if (!attendanceDate || !status) {
      setAttendanceMessage(
        "Select a date and attendance status."
      );
      return;
    }

    if (savedAttendance[id]) {
      setAttendanceMessage(
        "Attendance is already saved for this student."
      );
      return;
    }

    try {
      setAttendanceSubmitting(true);
      setAttendanceMessage("");

      const response = await api.post("/teacher/attendance", {
        student_id: id,
        attendance_date: attendanceDate,
        status,
      });

      setSavedAttendance((previous) => ({
        ...previous,
        [id]: status,
      }));

      setAttendanceStatus((previous) => ({
        ...previous,
        [id]: "",
      }));

      setAttendanceMessage(
        response.data.message ||
          "Attendance saved successfully."
      );
    } catch (err) {
      setAttendanceMessage(
        err.response?.data?.detail ||
          "Unable to save attendance."
      );
    } finally {
      setAttendanceSubmitting(false);
    }
  }

  // UPLOAD STUDENT MARKS
  async function handleUploadMarks(event) {
    event.preventDefault();
    setMarksMessage("");

    if (
      !studentId ||
      !examId ||
      !subjectId ||
      marksObtained === "" ||
      maxMarks === ""
    ) {
      setMarksMessage("Please fill in all marks details.");
      return;
    }

    if (
      Number(marksObtained) < 0 ||
      Number(maxMarks) <= 0 ||
      Number(marksObtained) > Number(maxMarks)
    ) {
      setMarksMessage(
        "Enter valid marks. Obtained marks cannot exceed maximum marks."
      );
      return;
    }

    try {
      setMarksSubmitting(true);

      const response = await api.post("/teacher/marks", {
        student_id: Number(studentId),
        exam_id: Number(examId),
        subject_id: Number(subjectId),
        marks_obtained: Number(marksObtained),
        max_marks: Number(maxMarks),
      });

      setMarksMessage(
        response.data.message || "Marks uploaded successfully."
      );

      setStudentId("");
      setExamId("");
      setSubjectId("");
      setMarksObtained("");
      setMaxMarks("");
    } catch (err) {
      setMarksMessage(
        err.response?.data?.detail ||
          "Unable to upload marks."
      );
    } finally {
      setMarksSubmitting(false);
    }
  }

  if (loading) {
    return (
      <main className="teacher-dashboard">
        <div className="teacher-loading-card">
          Loading your dashboard...
        </div>
      </main>
    );
  }

  return (
    <main className="teacher-dashboard">
      <header className="teacher-page-header">
        <div>
          <p className="teacher-eyebrow">TEACHER PORTAL</p>
          <h1>Teacher Dashboard</h1>
          <p className="teacher-subtitle">
            Manage your students, attendance and examination marks.
          </p>
        </div>

        <div className="teacher-header-mark">T</div>
      </header>

      {error && (
        <div className="teacher-alert teacher-alert-error">
          {error}
        </div>
      )}

      {/* MY PROFILE */}

      <section className="teacher-profile-card">
        <div className="teacher-profile-icon">
          <span>TP</span>
        </div>

        <div>
          <p className="teacher-card-kicker">YOUR WORKSPACE</p>
          <h2>My Profile</h2>
          <p>
            Welcome to your teacher portal. Your assigned classes
            and tools are available below.
          </p>
        </div>
      </section>

      {/* MY STUDENTS */}

      <section className="teacher-section">
        <div className="teacher-section-heading">
          <div>
            <p className="teacher-card-kicker">CLASSROOM</p>
            <h2>My Students</h2>
            <p>Students assigned to your classes.</p>
          </div>

          <span className="teacher-count-badge">
            {students.length} students
          </span>
        </div>

        {students.length === 0 ? (
          <div className="teacher-empty-state">
            No students are assigned to your classes yet.
          </div>
        ) : (
          <div className="teacher-table-wrap">
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Student name</th>
                  <th>Roll number</th>
                  <th>Class ID</th>
                </tr>
              </thead>

              <tbody>
                {students.map((student) => (
                  <tr key={student.id}>
                    <td className="teacher-student-name">
                      {student.name}
                    </td>
                    <td>{student.roll_no}</td>
                    <td>
                      <span className="teacher-class-chip">
                        Class {student.class_id}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* STUDENT ATTENDANCE */}

      <section className="teacher-section">
        <div className="teacher-section-heading">
          <div>
            <p className="teacher-card-kicker">DAILY CLASSWORK</p>
            <h2>Student Attendance</h2>
            <p>
              Choose a date, mark each student's status and save it.
            </p>
          </div>
        </div>

        <div className="teacher-date-control">
          <label htmlFor="teacher-attendance-date">
            Attendance date
          </label>

          <input
            id="teacher-attendance-date"
            className="teacher-input"
            type="date"
            value={attendanceDate}
            onChange={(event) =>
              setAttendanceDate(event.target.value)
            }
          />
        </div>

        {attendanceLoading && (
          <div className="teacher-empty-state">
            Loading attendance records...
          </div>
        )}

        {!attendanceLoading && students.length === 0 ? (
          <div className="teacher-empty-state">
            There are no assigned students to mark.
          </div>
        ) : (
          !attendanceLoading && (
            <div className="teacher-attendance-list">
              {students.map((student) => {
                const savedStatus = savedAttendance[student.id];

                return (
                  <div
                    className="teacher-attendance-row"
                    key={student.id}
                  >
                    <div className="teacher-attendance-student">
                      <div className="teacher-student-avatar">
                        {student.name?.charAt(0)?.toUpperCase() || "S"}
                      </div>

                      <div>
                        <strong>{student.name}</strong>
                        <span>Roll No: {student.roll_no}</span>
                      </div>
                    </div>

                    <div className="teacher-attendance-actions">
                      {savedStatus ? (
                        <span className="teacher-class-chip">
                          {savedStatus.charAt(0).toUpperCase() +
                            savedStatus.slice(1)}{" "}
                          - Saved
                        </span>
                      ) : (
                        <>
                          <label
                            className="teacher-sr-only"
                            htmlFor={`attendance-${student.id}`}
                          >
                            Attendance status for {student.name}
                          </label>

                          <select
                            id={`attendance-${student.id}`}
                            className="teacher-input teacher-status-select"
                            value={attendanceStatus[student.id] || ""}
                            onChange={(event) =>
                              handleStatusChange(
                                student.id,
                                event.target.value
                              )
                            }
                          >
                            <option value="">Select status</option>
                            <option value="present">Present</option>
                            <option value="absent">Absent</option>
                            <option value="late">Late</option>
                          </select>

                          <button
                            className="teacher-button teacher-button-primary"
                            type="button"
                            disabled={attendanceSubmitting}
                            onClick={() =>
                              handleSubmitAttendance(student.id)
                            }
                          >
                            {attendanceSubmitting
                              ? "Saving..."
                              : "Save attendance"}
                          </button>
                        </>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )
        )}

        {attendanceMessage && (
          <div
            className="teacher-alert teacher-alert-info"
            role="status"
          >
            {attendanceMessage}
          </div>
        )}
      </section>

      {/* UPLOAD MARKS */}

      <section className="teacher-section">
        <div className="teacher-section-heading">
          <div>
            <p className="teacher-card-kicker">ASSESSMENTS</p>
            <h2>Upload Student Marks</h2>
            <p>
              Record examination marks for a student and subject.
            </p>
          </div>
        </div>

        <form
          className="teacher-marks-form"
          onSubmit={handleUploadMarks}
        >
          <div className="teacher-form-field">
            <label htmlFor="marks-student">Select student</label>

            <select
              id="marks-student"
              className="teacher-input"
              value={studentId}
              onChange={(event) =>
                setStudentId(event.target.value)
              }
            >
              <option value="">Choose a student</option>

              {students.map((student) => (
                <option key={student.id} value={student.id}>
                  {student.name} - {student.roll_no}
                </option>
              ))}
            </select>
          </div>

          <div className="teacher-form-field">
            <label htmlFor="marks-exam">Select exam</label>

            <select
              id="marks-exam"
              className="teacher-input"
              value={examId}
              onChange={(event) =>
                setExamId(event.target.value)
              }
            >
              <option value="">Choose an exam</option>

              {exams.map((exam) => (
                <option key={exam.id} value={exam.id}>
                  {exam.exam_name}
                </option>
              ))}
            </select>
          </div>

          <div className="teacher-form-field">
            <label htmlFor="marks-subject">Select subject</label>

            <select
              id="marks-subject"
              className="teacher-input"
              value={subjectId}
              onChange={(event) =>
                setSubjectId(event.target.value)
              }
            >
              <option value="">Choose a subject</option>

              {subjects.map((subject) => (
                <option key={subject.id} value={subject.id}>
                  {subject.subject_name}
                </option>
              ))}
            </select>
          </div>

          <div className="teacher-form-field">
            <label htmlFor="marks-obtained">
              Marks obtained
            </label>

            <input
              id="marks-obtained"
              className="teacher-input"
              type="number"
              min="0"
              step="0.01"
              value={marksObtained}
              onChange={(event) =>
                setMarksObtained(event.target.value)
              }
              placeholder="e.g. 85"
            />
          </div>

          <div className="teacher-form-field">
            <label htmlFor="marks-maximum">
              Maximum marks
            </label>

            <input
              id="marks-maximum"
              className="teacher-input"
              type="number"
              min="0.01"
              step="0.01"
              value={maxMarks}
              onChange={(event) =>
                setMaxMarks(event.target.value)
              }
              placeholder="e.g. 100"
            />
          </div>

          <div className="teacher-form-submit">
            <button
              className="teacher-button teacher-button-primary"
              type="submit"
              disabled={marksSubmitting}
            >
              {marksSubmitting ? "Uploading..." : "Upload marks"}
            </button>
          </div>
        </form>

        {marksMessage && (
          <div
            className="teacher-alert teacher-alert-info"
            role="status"
          >
            {marksMessage}
          </div>
        )}
      </section>

      {/* TEACHER'S OWN ATTENDANCE HISTORY */}

      <section className="teacher-section teacher-own-attendance">
        <div className="teacher-section-heading">
          <div>
            <p className="teacher-card-kicker">YOUR RECORDS</p>
            <h2>My Attendance</h2>
            <p>View your own attendance records.</p>
          </div>

          <span className="teacher-count-badge">
            {ownAttendance.length} records
          </span>
        </div>

        {ownAttendanceLoading ? (
          <div className="teacher-empty-state">
            Loading your attendance history...
          </div>
        ) : ownAttendanceError ? (
          <div className="teacher-alert teacher-alert-error">
            {ownAttendanceError}
          </div>
        ) : ownAttendance.length === 0 ? (
          <div className="teacher-empty-state">
            No attendance records found.
          </div>
        ) : (
          <div className="teacher-table-wrap">
            <table className="teacher-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Attendance status</th>
                </tr>
              </thead>

              <tbody>
                {ownAttendance.map((record, index) => (
                  <tr key={`${record.date}-${index}`}>
                    <td>{record.date}</td>
                    <td>
                      <span className="teacher-class-chip">
                        {record.status.charAt(0).toUpperCase() +
                          record.status.slice(1)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <footer className="teacher-dashboard-footer">
        Teacher Portal <span>•</span> School Management System
      </footer>
    </main>
  );
}

export default TeacherDashboard;
