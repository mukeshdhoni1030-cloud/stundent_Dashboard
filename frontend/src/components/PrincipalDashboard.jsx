import { useEffect, useRef, useState } from "react";
import api from "../services/api";

function PrincipalDashboard() {
  // =====================================
  // DASHBOARD STATE
  // =====================================

  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  const [dashboardError, setDashboardError] = useState("");

  const [studentMessage, setStudentMessage] = useState("");
  const [studentError, setStudentError] = useState("");

  const [teacherMessage, setTeacherMessage] = useState("");
  const [teacherError, setTeacherError] = useState("");

  // =====================================
  // STUDENT MANAGEMENT STATE
  // =====================================

  const [students, setStudents] = useState([]);
  const [studentsLoading, setStudentsLoading] = useState(false);
  const [editingStudentId, setEditingStudentId] = useState(null);

  const emptyForm = {
    email: "",
    password: "",
    name: "",
    class_id: "",
    roll_no: "",
    parent_name: "",
    parent_phone: "",
  };

  const [studentForm, setStudentForm] = useState(emptyForm);

  // =====================================
  // TEACHER MANAGEMENT STATE
  // =====================================

  const [teachers, setTeachers] = useState([]);
  const [teachersLoading, setTeachersLoading] = useState(false);
  const [editingTeacherId, setEditingTeacherId] = useState(null);

  const emptyTeacherForm = {
    email: "",
    password: "",
    name: "",
    qualification: "",
    phone: "",
  };

  const [teacherForm, setTeacherForm] = useState(emptyTeacherForm);

  // =====================================
  // STUDENT ATTENDANCE STATE
  // =====================================

  const [studentAttendance, setStudentAttendance] = useState([]);
  const [attendanceLoading, setAttendanceLoading] = useState(false);

  // =====================================
  // TEACHER ATTENDANCE STATE
  // =====================================

  const [teacherAttendance, setTeacherAttendance] = useState([]);
  const [teacherAttendanceLoading, setTeacherAttendanceLoading] = useState(false);
  const [teacherAttendanceForm, setTeacherAttendanceForm] = useState({
    teacher_id: "",
    attendance_date: new Date().toISOString().slice(0, 10),
    status: "present",
  });
  const [teacherAttendanceSaving, setTeacherAttendanceSaving] = useState(false);
  const [teacherAttendanceMessage, setTeacherAttendanceMessage] = useState("");
  const [teacherAttendanceError, setTeacherAttendanceError] = useState("");

  // =====================================
  // STUDENT FEES STATE
  // =====================================

  const [fees, setFees] = useState([]);
  const [feesLoading, setFeesLoading] = useState(false);

  // =====================================
  // EMPLOYEE SALARIES STATE
  // =====================================

  const [salaries, setSalaries] = useState([]);
  const [salariesLoading, setSalariesLoading] = useState(false);

  const [salaryForm, setSalaryForm] = useState({
    teacher_id: "",
    salary_month: new Date().toISOString().slice(0, 7),
    amount: "",
  });
  const [salarySaving, setSalarySaving] = useState(false);
  const [salaryMessage, setSalaryMessage] = useState("");
  const [salaryError, setSalaryError] = useState("");

  // Sections below the initial dashboard are loaded only when they approach
  // the viewport. This avoids sending every API request immediately at login.
  const studentAttendanceSectionRef = useRef(null);
  const teacherAttendanceSectionRef = useRef(null);
  const feesSectionRef = useRef(null);
  const salariesSectionRef = useRef(null);

  // =====================================
  // FETCH DASHBOARD
  // =====================================

  async function fetchDashboard() {
    try {
      const response = await api.get("/principal/dashboard");
      setDashboard(response.data);
    } catch (err) {
      setDashboardError(
        err.response?.data?.detail ||
        "Unable to load dashboard statistics."
      );
    }
  }

  // =====================================
  // FETCH STUDENTS
  // =====================================

  async function fetchStudents() {
    try {
      setStudentsLoading(true);

      const response = await api.get("/principal/students");
      setStudents(response.data);
    } catch (err) {
      setDashboardError(
        err.response?.data?.detail ||
        "Unable to load students."
      );
    } finally {
      setStudentsLoading(false);
      setLoading(false);
    }
  }

  // =====================================
  // FETCH TEACHERS
  // =====================================

  async function fetchTeachers() {
    try {
      setTeachersLoading(true);

      const response = await api.get("/principal/teachers");
      setTeachers(response.data);
    } catch (err) {
      setDashboardError(
        err.response?.data?.detail ||
        "Unable to load teachers."
      );
    } finally {
      setTeachersLoading(false);
    }
  }

  // =====================================
  // FETCH STUDENT ATTENDANCE
  // =====================================

  async function fetchStudentAttendance() {
    try {
      setAttendanceLoading(true);

      const response = await api.get("/principal/student-attendance");
      setStudentAttendance(response.data);
    } catch (err) {
      setDashboardError(
        err.response?.data?.detail ||
        "Unable to load student attendance."
      );
    } finally {
      setAttendanceLoading(false);
    }
  }

  // =====================================
  // FETCH TEACHER ATTENDANCE
  // =====================================

  async function fetchTeacherAttendance() {
    try {
      setTeacherAttendanceLoading(true);

      const response = await api.get("/principal/teacher-attendance");
      setTeacherAttendance(response.data);
    } catch (err) {
      setDashboardError(
        err.response?.data?.detail ||
        "Unable to load teacher attendance."
      );
    } finally {
      setTeacherAttendanceLoading(false);
    }
  }

  // =====================================
  // FETCH STUDENT FEES
  // =====================================

  async function fetchFees() {
    try {
      setFeesLoading(true);

      const response = await api.get("/principal/fees");
      setFees(response.data);
    } catch (err) {
      setDashboardError(
        err.response?.data?.detail ||
        "Unable to load student fees."
      );
    } finally {
      setFeesLoading(false);
    }
  }

  // =====================================
  // FETCH EMPLOYEE SALARIES
  // =====================================

  async function fetchSalaries() {
    try {
      setSalariesLoading(true);

      const response = await api.get("/principal/salaries");
      setSalaries(response.data);
    } catch (err) {
      setDashboardError(
        err.response?.data?.detail ||
        "Unable to load employee salaries."
      );
    } finally {
      setSalariesLoading(false);
    }
  }

  // =====================================
  // LOAD ALL DASHBOARD DATA
  // =====================================

  useEffect(() => {
    // Load only the data needed for the first visible dashboard sections.
    fetchDashboard();
    fetchStudents();
    fetchTeachers();
  }, []);

  useEffect(() => {
    const lazySections = [
      {
        element: studentAttendanceSectionRef.current,
        load: fetchStudentAttendance,
      },
      {
        element: teacherAttendanceSectionRef.current,
        load: fetchTeacherAttendance,
      },
      {
        element: feesSectionRef.current,
        load: fetchFees,
      },
      {
        element: salariesSectionRef.current,
        load: fetchSalaries,
      },
    ];

    if (typeof IntersectionObserver === "undefined") {
      lazySections.forEach((section) => section.load());
      return undefined;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;

          const section = lazySections.find(
            (item) => item.element === entry.target
          );

          if (section) {
            observer.unobserve(entry.target);
            section.load();
          }
        });
      },
      {
        // Start loading shortly before the user reaches each section.
        rootMargin: "300px 0px",
      }
    );

    lazySections.forEach((section) => {
      if (section.element) observer.observe(section.element);
    });

    return () => observer.disconnect();
  }, []);

  // =====================================
  // STUDENT FORM HANDLING
  // =====================================

  function handleInputChange(event) {
    const { name, value } = event.target;

    setStudentForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  // =====================================
  // ADD OR UPDATE STUDENT
  // =====================================

  async function handleStudentSubmit(event) {
    event.preventDefault();

    setStudentMessage("");
    setStudentError("");

    try {
      if (editingStudentId) {
        const updateData = {
          name: studentForm.name,
          class_id: Number(studentForm.class_id),
          roll_no: studentForm.roll_no,
          parent_name: studentForm.parent_name,
          parent_phone: studentForm.parent_phone,
        };

        const response = await api.put(
          `/principal/students/${editingStudentId}`,
          updateData
        );

        setStudentMessage(
          response.data.message || "Student updated successfully."
        );
      } else {
        const response = await api.post(
          "/principal/students",
          {
            ...studentForm,
            class_id: Number(studentForm.class_id),
          }
        );

        setStudentMessage(
          response.data.message || "Student created successfully."
        );
      }

      setStudentForm(emptyForm);
      setEditingStudentId(null);

      await fetchStudents();
      await fetchDashboard();

    } catch (err) {
      setStudentError(
        err.response?.data?.detail ||
        "Unable to save student details."
      );
    }
  }

  // =====================================
  // EDIT STUDENT
  // =====================================

  function handleEditStudent(student) {
    setEditingStudentId(student.id);

    setStudentForm({
      email: student.email,
      password: "",
      name: student.name,
      class_id: String(student.class_id),
      roll_no: student.roll_no,
      parent_name: student.parent_name,
      parent_phone: student.parent_phone,
    });

    setStudentMessage("");
    setStudentError("");
  }

  // =====================================
  // CANCEL STUDENT EDIT
  // =====================================

  function handleCancelEdit() {
    setEditingStudentId(null);
    setStudentForm(emptyForm);
    setStudentMessage("");
    setStudentError("");
  }

  // =====================================
  // DELETE STUDENT
  // =====================================

  async function handleDeleteStudent(studentId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this student?"
    );

    if (!confirmed) return;

    setStudentMessage("");
    setStudentError("");

    try {
      const response = await api.delete(
        `/principal/students/${studentId}`
      );

      setStudentMessage(
        response.data.message || "Student deleted successfully."
      );

      await fetchStudents();
      await fetchDashboard();

    } catch (err) {
      setStudentError(
        err.response?.data?.detail ||
        "Unable to delete student."
      );
    }
  }

  // =====================================
  // TEACHER FORM HANDLING
  // =====================================

  function handleTeacherInputChange(event) {
    const { name, value } = event.target;

    setTeacherForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  // =====================================
  // ADD OR UPDATE TEACHER
  // =====================================

  async function handleTeacherSubmit(event) {
    event.preventDefault();

    setTeacherMessage("");
    setTeacherError("");

    try {
      if (editingTeacherId) {
        const updateData = {
          name: teacherForm.name,
          qualification: teacherForm.qualification,
          phone: teacherForm.phone,
        };

        const response = await api.put(
          `/principal/teachers/${editingTeacherId}`,
          updateData
        );

        setTeacherMessage(
          response.data.message || "Teacher updated successfully."
        );
      } else {
        const response = await api.post(
          "/principal/teachers",
          teacherForm
        );

        setTeacherMessage(
          response.data.message || "Teacher created successfully."
        );
      }

      setTeacherForm(emptyTeacherForm);
      setEditingTeacherId(null);

      await fetchTeachers();
      await fetchDashboard();

    } catch (err) {
      setTeacherError(
        err.response?.data?.detail ||
        "Unable to save teacher details."
      );
    }
  }

  // =====================================
  // EDIT TEACHER
  // =====================================

  function handleEditTeacher(teacher) {
    setEditingTeacherId(teacher.id);

    setTeacherForm({
      email: teacher.email,
      password: "",
      name: teacher.name,
      qualification: teacher.qualification,
      phone: teacher.phone,
    });

    setTeacherMessage("");
    setTeacherError("");
  }

  // =====================================
  // CANCEL TEACHER EDIT
  // =====================================

  function handleCancelTeacherEdit() {
    setEditingTeacherId(null);
    setTeacherForm(emptyTeacherForm);
    setTeacherMessage("");
    setTeacherError("");
  }

  // =====================================
  // DELETE TEACHER
  // =====================================

  async function handleDeleteTeacher(teacherId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this teacher?"
    );

    if (!confirmed) return;

    setTeacherMessage("");
    setTeacherError("");

    try {
      const response = await api.delete(
        `/principal/teachers/${teacherId}`
      );

      setTeacherMessage(
        response.data.message || "Teacher deleted successfully."
      );

      await fetchTeachers();
      await fetchDashboard();

    } catch (err) {
      setTeacherError(
        err.response?.data?.detail ||
        "Unable to delete teacher."
      );
    }
  }

  // =====================================
  // MARK TEACHER ATTENDANCE
  // =====================================

  function handleTeacherAttendanceInputChange(event) {
    const { name, value } = event.target;

    setTeacherAttendanceForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleTeacherAttendanceSubmit(event) {
    event.preventDefault();

    setTeacherAttendanceMessage("");
    setTeacherAttendanceError("");

    if (!teacherAttendanceForm.teacher_id) {
      setTeacherAttendanceError("Please select a teacher.");
      return;
    }

    try {
      setTeacherAttendanceSaving(true);

      const response = await api.post("/principal/teacher-attendance", {
        teacher_id: Number(teacherAttendanceForm.teacher_id),
        attendance_date: teacherAttendanceForm.attendance_date,
        status: teacherAttendanceForm.status,
      });

      setTeacherAttendanceMessage(
        response.data.message || "Teacher attendance marked successfully."
      );

      setTeacherAttendanceForm((previous) => ({
        ...previous,
        teacher_id: "",
        status: "present",
      }));

      await fetchTeacherAttendance();
    } catch (err) {
      setTeacherAttendanceError(
        err.response?.data?.detail ||
        "Unable to mark teacher attendance."
      );
    } finally {
      setTeacherAttendanceSaving(false);
    }
  }

  // =====================================
  // ADD EMPLOYEE SALARY
  // =====================================

  function handleSalaryInputChange(event) {
    const { name, value } = event.target;

    setSalaryForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleSalarySubmit(event) {
    event.preventDefault();

    setSalaryMessage("");
    setSalaryError("");

    if (!salaryForm.teacher_id) {
      setSalaryError("Please select a teacher.");
      return;
    }

    try {
      setSalarySaving(true);

      const response = await api.post("/principal/salaries", {
        teacher_id: Number(salaryForm.teacher_id),
        salary_month: `${salaryForm.salary_month}-01`,
        amount: Number(salaryForm.amount),
      });

      setSalaryMessage(
        response.data.message || "Salary created successfully."
      );

      setSalaryForm((previous) => ({
        ...previous,
        teacher_id: "",
        amount: "",
      }));

      await fetchSalaries();
    } catch (err) {
      setSalaryError(
        err.response?.data?.detail ||
        "Unable to save salary details."
      );
    } finally {
      setSalarySaving(false);
    }
  }

  // =====================================
  // DASHBOARD UI
  // =====================================

  return (
    <div className="principal-dashboard">

      <header className="principal-header">
        <h1>Principal Dashboard</h1>
        <p>Welcome to your school administration portal.</p>
        {dashboardError && (
          <p className="error-message">{dashboardError}</p>
        )}
      </header>

      {/* DASHBOARD STATISTICS */}

      <section className="principal-section">
        <h2>School Overview</h2>

        {loading && <p>Loading statistics...</p>}

        {dashboard && (
          <div className="principal-stats">

            <div className="principal-stat-card">
              <h3>Total Students</h3>
              <h1>{dashboard.total_students}</h1>
            </div>

            <div className="principal-stat-card">
              <h3>Total Teachers</h3>
              <h1>{dashboard.total_teachers}</h1>
            </div>

          </div>
        )}
      </section>

      {/* =====================================
          STUDENT MANAGEMENT
      ===================================== */}

      <section className="principal-section">

        <h2>Student Management</h2>

        <div className="student-form-container">

          <h3>
            {editingStudentId ? "Edit Student" : "Add New Student"}
          </h3>

          <form
            className="student-form"
            onSubmit={handleStudentSubmit}
          >

            <input
              type="text"
              name="name"
              placeholder="Student Name"
              value={studentForm.name}
              onChange={handleInputChange}
              required
            />

            <input
              type="email"
              name="email"
              placeholder="Student Email"
              value={studentForm.email}
              onChange={handleInputChange}
              disabled={Boolean(editingStudentId)}
              required
            />

            {!editingStudentId && (
              <input
                type="password"
                name="password"
                placeholder="Student Password"
                value={studentForm.password}
                onChange={handleInputChange}
                minLength="6"
                required
              />
            )}

            <input
              type="number"
              name="class_id"
              placeholder="Class ID"
              value={studentForm.class_id}
              onChange={handleInputChange}
              min="1"
              required
            />

            <input
              type="text"
              name="roll_no"
              placeholder="Roll Number"
              value={studentForm.roll_no}
              onChange={handleInputChange}
              required
            />

            <input
              type="text"
              name="parent_name"
              placeholder="Parent Name"
              value={studentForm.parent_name}
              onChange={handleInputChange}
              required
            />

            <input
              type="tel"
              name="parent_phone"
              placeholder="Parent Phone"
              value={studentForm.parent_phone}
              onChange={handleInputChange}
              required
            />

            <div className="student-form-actions">

              <button type="submit" className="primary-btn">
                {editingStudentId ? "Update Student" : "Add Student"}
              </button>

              {editingStudentId && (
                <button
                  type="button"
                  className="secondary-btn"
                  onClick={handleCancelEdit}
                >
                  Cancel Edit
                </button>
              )}

            </div>

          </form>
        </div>

        {/* COMMON MESSAGES */}

        {studentMessage && (
          <p className="success-message">{studentMessage}</p>
        )}

        {studentError && (
          <p className="error-message">{studentError}</p>
        )}

        {/* ALL STUDENTS */}

        <div className="student-list-container">

          <div className="student-list-header">
            <h3>All Students</h3>

            <button
              type="button"
              className="primary-btn refresh-btn"
              onClick={fetchStudents}
              disabled={studentsLoading}
            >
              {studentsLoading ? "Refreshing..." : "Refresh Students"}
            </button>
          </div>

          {studentsLoading && <p>Loading students...</p>}

          {!studentsLoading && students.length === 0 && (
            <p>No students found.</p>
          )}

          {!studentsLoading && students.length > 0 && (
            <div className="student-table-wrapper">

              <table className="student-table">

                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Roll No</th>
                    <th>Class ID</th>
                    <th>Parent Name</th>
                    <th>Phone</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {students.map((student) => (
                    <tr key={student.id}>

                      <td>{student.name}</td>
                      <td>{student.email}</td>
                      <td>{student.roll_no}</td>
                      <td>{student.class_id}</td>
                      <td>{student.parent_name}</td>
                      <td>{student.parent_phone}</td>

                      <td>
                        <div className="student-actions">

                          <button
                            type="button"
                            className="edit-btn"
                            onClick={() => handleEditStudent(student)}
                          >
                            Edit
                          </button>

                          <button
                            type="button"
                            className="delete-btn"
                            onClick={() => handleDeleteStudent(student.id)}
                          >
                            Delete
                          </button>

                        </div>
                      </td>

                    </tr>
                  ))}
                </tbody>

              </table>
            </div>
          )}

        </div>
      </section>

      {/* =====================================
          TEACHER MANAGEMENT
      ===================================== */}

      <section className="principal-section">

        <h2>Teacher Management</h2>

        <div className="student-form-container">

          <h3>
            {editingTeacherId ? "Edit Teacher" : "Add New Teacher"}
          </h3>

          <form
            className="student-form"
            onSubmit={handleTeacherSubmit}
          >

            <input
              type="text"
              name="name"
              placeholder="Teacher Name"
              value={teacherForm.name}
              onChange={handleTeacherInputChange}
              required
            />

            <input
              type="email"
              name="email"
              placeholder="Teacher Email"
              value={teacherForm.email}
              onChange={handleTeacherInputChange}
              disabled={Boolean(editingTeacherId)}
              required
            />

            {!editingTeacherId && (
              <input
                type="password"
                name="password"
                placeholder="Teacher Password"
                value={teacherForm.password}
                onChange={handleTeacherInputChange}
                minLength="6"
                required
              />
            )}

            <input
              type="text"
              name="qualification"
              placeholder="Qualification"
              value={teacherForm.qualification}
              onChange={handleTeacherInputChange}
              required
            />

            <input
              type="tel"
              name="phone"
              placeholder="Phone Number"
              value={teacherForm.phone}
              onChange={handleTeacherInputChange}
              required
            />

            <div className="student-form-actions">

              <button type="submit" className="primary-btn">
                {editingTeacherId ? "Update Teacher" : "Add Teacher"}
              </button>

              {editingTeacherId && (
                <button
                  type="button"
                  className="secondary-btn"
                  onClick={handleCancelTeacherEdit}
                >
                  Cancel Edit
                </button>
              )}

            </div>

          </form>
        </div>

        {teacherMessage && (
          <p className="success-message">{teacherMessage}</p>
        )}

        {teacherError && (
          <p className="error-message">{teacherError}</p>
        )}

        {/* ALL TEACHERS */}

        <div className="student-list-container">

          <div className="student-list-header">
            <h3>All Teachers</h3>

            <button
              type="button"
              className="primary-btn refresh-btn"
              onClick={fetchTeachers}
              disabled={teachersLoading}
            >
              {teachersLoading ? "Refreshing..." : "Refresh Teachers"}
            </button>
          </div>

          {teachersLoading && <p>Loading teachers...</p>}

          {!teachersLoading && teachers.length === 0 && (
            <p>No teachers found.</p>
          )}

          {!teachersLoading && teachers.length > 0 && (
            <div className="student-table-wrapper">

              <table className="student-table">

                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Qualification</th>
                    <th>Phone</th>
                    <th>Actions</th>
                  </tr>
                </thead>

                <tbody>
                  {teachers.map((teacher) => (
                    <tr key={teacher.id}>

                      <td>{teacher.name}</td>
                      <td>{teacher.email}</td>
                      <td>{teacher.qualification}</td>
                      <td>{teacher.phone}</td>

                      <td>
                        <div className="student-actions">

                          <button
                            type="button"
                            className="edit-btn"
                            onClick={() => handleEditTeacher(teacher)}
                          >
                            Edit
                          </button>

                          <button
                            type="button"
                            className="delete-btn"
                            onClick={() => handleDeleteTeacher(teacher.id)}
                          >
                            Delete
                          </button>

                        </div>
                      </td>

                    </tr>
                  ))}
                </tbody>

              </table>
            </div>
          )}

        </div>
      </section>

      {/* =====================================
          STUDENT ATTENDANCE
      ===================================== */}

      <section className="principal-section" ref={studentAttendanceSectionRef}>
        <h2>Student Attendance</h2>
        <p>Monitor student attendance records.</p>

        <div className="student-list-container">
          <div className="student-list-header">
            <h3>Attendance Records</h3>

            <button
              type="button"
              className="primary-btn refresh-btn"
              onClick={fetchStudentAttendance}
              disabled={attendanceLoading}
            >
              {attendanceLoading ? "Refreshing..." : "Refresh Attendance"}
            </button>
          </div>

          {attendanceLoading && <p>Loading student attendance...</p>}

          {!attendanceLoading && studentAttendance.length === 0 && (
            <p>No student attendance records found.</p>
          )}

          {!attendanceLoading && studentAttendance.length > 0 && (
            <div className="student-table-wrapper">
              <table className="student-table">
                <thead>
                  <tr>
                    <th>Student ID</th>
                    <th>Student Name</th>
                    <th>Date</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  {studentAttendance.map((record, index) => (
                    <tr
                      key={`${record.student_id}-${record.date}-${index}`}
                    >
                      <td>{record.student_id}</td>
                      <td>{record.student_name}</td>
                      <td>{record.date}</td>
                      <td>
                        <span
                          style={{
                            color:
                              String(record.status).toLowerCase() === "present"
                                ? "#16a34a"
                                : "#dc2626",
                            fontWeight: "600",
                            textTransform: "capitalize",
                          }}
                        >
                          {record.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>

      {/* =====================================
          TEACHER ATTENDANCE
      ===================================== */}

      <section className="principal-section" ref={teacherAttendanceSectionRef}>
        <h2>Teacher Attendance</h2>
        <p>Monitor teacher attendance records.</p>

        <div className="student-form-container">
          <h3>Mark Teacher Attendance</h3>

          <form
            className="student-form"
            onSubmit={handleTeacherAttendanceSubmit}
          >
            <select
              name="teacher_id"
              value={teacherAttendanceForm.teacher_id}
              onChange={handleTeacherAttendanceInputChange}
              required
            >
              <option value="">Select Teacher</option>
              {teachers.map((teacher) => (
                <option key={teacher.id} value={teacher.id}>
                  {teacher.name} (ID: {teacher.id})
                </option>
              ))}
            </select>

            <input
              type="date"
              name="attendance_date"
              value={teacherAttendanceForm.attendance_date}
              onChange={handleTeacherAttendanceInputChange}
              required
            />

            <select
              name="status"
              value={teacherAttendanceForm.status}
              onChange={handleTeacherAttendanceInputChange}
              required
            >
              <option value="present">Present</option>
              <option value="absent">Absent</option>
              <option value="late">Late</option>
            </select>

            <div className="student-form-actions">
              <button
                type="submit"
                className="primary-btn"
                disabled={teacherAttendanceSaving || teachers.length === 0}
              >
                {teacherAttendanceSaving ? "Saving Attendance..." : "Mark Attendance"}
              </button>
            </div>
          </form>

          {teachers.length === 0 && (
            <p className="error-message">
              Add a teacher before marking attendance.
            </p>
          )}

          {teacherAttendanceMessage && (
            <p className="success-message">{teacherAttendanceMessage}</p>
          )}

          {teacherAttendanceError && (
            <p className="error-message">{teacherAttendanceError}</p>
          )}
        </div>

        <div className="student-list-container">
          <div className="student-list-header">
            <h3>Teacher Attendance Records</h3>

            <button
              type="button"
              className="primary-btn refresh-btn"
              onClick={fetchTeacherAttendance}
              disabled={teacherAttendanceLoading}
            >
              {teacherAttendanceLoading
                ? "Refreshing..."
                : "Refresh Attendance"}
            </button>
          </div>

          {teacherAttendanceLoading && (
            <p>Loading teacher attendance...</p>
          )}

          {!teacherAttendanceLoading && teacherAttendance.length === 0 && (
            <p>No teacher attendance records found.</p>
          )}

          {!teacherAttendanceLoading && teacherAttendance.length > 0 && (
            <div className="student-table-wrapper">
              <table className="student-table">
                <thead>
                  <tr>
                    <th>Teacher ID</th>
                    <th>Teacher Name</th>
                    <th>Date</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  {teacherAttendance.map((record, index) => (
                    <tr
                      key={`${record.teacher_id}-${record.date}-${index}`}
                    >
                      <td>{record.teacher_id}</td>
                      <td>{record.teacher_name}</td>
                      <td>{record.date}</td>
                      <td>
                        <span
                          style={{
                            color:
                              String(record.status).toLowerCase() === "present"
                                ? "#16a34a"
                                : "#dc2626",
                            fontWeight: "600",
                            textTransform: "capitalize",
                          }}
                        >
                          {record.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>

      {/* =====================================
          STUDENT FEES
      ===================================== */}

      <section className="principal-section" ref={feesSectionRef}>
        <h2>Student Fees</h2>
        <p>View student fee payments and pending balances.</p>

        <div className="student-list-container">
          <div className="student-list-header">
            <h3>Student Fee Records</h3>

            <button
              type="button"
              className="primary-btn refresh-btn"
              onClick={fetchFees}
              disabled={feesLoading}
            >
              {feesLoading ? "Refreshing..." : "Refresh Fees"}
            </button>
          </div>

          {feesLoading && <p>Loading student fees...</p>}

          {!feesLoading && fees.length === 0 && (
            <p>No student fee records found.</p>
          )}

          {!feesLoading && fees.length > 0 && (
            <div className="student-table-wrapper">
              <table className="student-table">
                <thead>
                  <tr>
                    <th>Student ID</th>
                    <th>Student Name</th>
                    <th>Total Fee</th>
                    <th>Paid Amount</th>
                    <th>Pending Amount</th>
                  </tr>
                </thead>

                <tbody>
                  {fees.map((record, index) => (
                    <tr key={`${record.student_id}-${index}`}>
                      <td>{record.student_id}</td>
                      <td>{record.student_name}</td>
                      <td>
                        ₹{Number(record.total_fee).toLocaleString("en-IN")}
                      </td>
                      <td style={{ color: "#16a34a", fontWeight: "600" }}>
                        ₹{Number(record.paid_amount).toLocaleString("en-IN")}
                      </td>
                      <td style={{ color: "#dc2626", fontWeight: "600" }}>
                        ₹{Number(record.pending_amount).toLocaleString("en-IN")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>

      {/* =====================================
          EMPLOYEE SALARIES
      ===================================== */}

      <section className="principal-section" ref={salariesSectionRef}>
        <h2>Employee Salaries</h2>
        <p>View teacher salary information.</p>

        <div className="student-form-container">
          <h3>Add New Salary</h3>

          <form
            className="student-form"
            onSubmit={handleSalarySubmit}
          >
            <select
              name="teacher_id"
              value={salaryForm.teacher_id}
              onChange={handleSalaryInputChange}
              required
            >
              <option value="">Select Teacher</option>
              {teachers.map((teacher) => (
                <option key={teacher.id} value={teacher.id}>
                  {teacher.name} (ID: {teacher.id})
                </option>
              ))}
            </select>

            <input
              type="month"
              name="salary_month"
              value={salaryForm.salary_month}
              onChange={handleSalaryInputChange}
              required
            />

            <input
              type="number"
              name="amount"
              placeholder="Salary Amount"
              value={salaryForm.amount}
              onChange={handleSalaryInputChange}
              min="0"
              step="0.01"
              required
            />

            <div className="student-form-actions">
              <button
                type="submit"
                className="primary-btn"
                disabled={salarySaving || teachers.length === 0}
              >
                {salarySaving ? "Saving Salary..." : "Save Salary"}
              </button>
            </div>
          </form>

          {teachers.length === 0 && (
            <p className="error-message">
              Add a teacher before creating a salary record.
            </p>
          )}

          {salaryMessage && (
            <p className="success-message">{salaryMessage}</p>
          )}

          {salaryError && (
            <p className="error-message">{salaryError}</p>
          )}
        </div>

        <div className="student-list-container">
          <div className="student-list-header">
            <h3>Employee Salary Records</h3>

            <button
              type="button"
              className="primary-btn refresh-btn"
              onClick={fetchSalaries}
              disabled={salariesLoading}
            >
              {salariesLoading ? "Refreshing..." : "Refresh Salaries"}
            </button>
          </div>

          {salariesLoading && <p>Loading employee salaries...</p>}

          {!salariesLoading && salaries.length === 0 && (
            <p>No salary records found.</p>
          )}

          {!salariesLoading && salaries.length > 0 && (
            <div className="student-table-wrapper">
              <table className="student-table">
                <thead>
                  <tr>
                    <th>Teacher ID</th>
                    <th>Teacher Name</th>
                    <th>Salary Month</th>
                    <th>Amount</th>
                  </tr>
                </thead>

                <tbody>
                  {salaries.map((record, index) => (
                    <tr key={`${record.teacher_id}-${record.salary_month}-${index}`}>
                      <td>{record.teacher_id}</td>
                      <td>{record.teacher_name}</td>
                      <td>{record.salary_month}</td>
                      <td style={{ fontWeight: "600" }}>
                        ₹{Number(record.amount).toLocaleString("en-IN")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>

    </div>
  );
}

export default PrincipalDashboard;