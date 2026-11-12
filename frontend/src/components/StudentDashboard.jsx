
import { useEffect, useState } from "react";
import api from "../services/api";

function StudentDashboard() {
  const [student, setStudent] = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [marks, setMarks] = useState([]);
  const [fees, setFees] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        setLoading(true);
        setError("");

        const [
          profileResponse,
          attendanceResponse,
          marksResponse,
          feesResponse,
        ] = await Promise.all([
          api.get("/student/me"),
          api.get("/student/attendance"),
          api.get("/student/marks"),
          api.get("/student/fees"),
        ]);

        setStudent(profileResponse.data);
        setAttendance(profileResponse.data ? attendanceResponse.data : []);
        setMarks(marksResponse.data);
        setFees(feesResponse.data);
      } catch (err) {
        setError(
          err.response?.data?.detail ||
            "Unable to load dashboard information."
        );
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  const formatCurrency = (value) =>
    `₹${Number(value || 0).toLocaleString("en-IN")}`;

  if (loading) {
    return (
      <div className="student-dashboard">
        <div className="student-loading">
          Loading student dashboard...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="student-dashboard">
        <div className="student-error">{error}</div>
      </div>
    );
  }

  const totalFees = fees.reduce(
    (sum, fee) => sum + Number(fee.total_fee || 0),
    0
  );

  const paidFees = fees.reduce(
    (sum, fee) => sum + Number(fee.paid_amount || 0),
    0
  );

  const pendingFees = fees.reduce(
    (sum, fee) => sum + Number(fee.pending_amount || 0),
    0
  );

  const attendancePercentage =
    attendance.length > 0
      ? (
          (attendance.filter(
            (record) =>
              record.status?.toLowerCase() === "present"
          ).length /
            attendance.length) *
          100
        ).toFixed(1)
      : "0";

  return (
    <div className="student-dashboard">
      <div className="student-welcome">
        <div>
          <p className="student-eyebrow">STUDENT PORTAL</p>
          <h1>Welcome, {student?.name || "Student"}!</h1>
          <p>Here is your academic overview.</p>
        </div>

        <div className="student-avatar">
          {student?.name?.charAt(0)?.toUpperCase() || "S"}
        </div>
      </div>

      {/* Summary Cards */}
      <div className="student-summary-grid">
        <div className="student-summary-card">
          <span>Attendance</span>
          <h2>{attendancePercentage}%</h2>
          <p>Based on available records</p>
        </div>

        <div className="student-summary-card">
          <span>Examinations</span>
          <h2>{marks.length}</h2>
          <p>Available subject results</p>
        </div>

        <div className="student-summary-card">
          <span>Total Fees</span>
          <h2>{formatCurrency(totalFees)}</h2>
          <p>Academic fee amount</p>
        </div>

        <div className="student-summary-card">
          <span>Pending Fees</span>
          <h2>{formatCurrency(pendingFees)}</h2>
          <p>Remaining payment</p>
        </div>
      </div>

      {/* Profile */}
      <section className="student-section">
        <div className="student-section-heading">
          <div>
            <h2>My Profile</h2>
            <p>Your personal information</p>
          </div>
        </div>

        <div className="student-profile-grid">
          <div className="student-profile-item">
            <span>Student Name</span>
            <strong>{student?.name || "N/A"}</strong>
          </div>

          <div className="student-profile-item">
            <span>Roll Number</span>
            <strong>{student?.roll_no || "N/A"}</strong>
          </div>

          <div className="student-profile-item">
            <span>Parent Name</span>
            <strong>{student?.parent_name || "N/A"}</strong>
          </div>

          <div className="student-profile-item">
            <span>Parent Phone</span>
            <strong>{student?.parent_phone || "N/A"}</strong>
          </div>
        </div>
      </section>

      {/* Attendance */}
      <section className="student-section">
        <div className="student-section-heading">
          <div>
            <h2>My Attendance</h2>
            <p>Your recorded attendance history</p>
          </div>
          <span className="student-count">
            {attendance.length} Records
          </span>
        </div>

        {attendance.length === 0 ? (
          <div className="student-empty">
            No attendance records available.
          </div>
        ) : (
          <div className="student-table-wrapper">
            <table className="student-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {attendance.map((record, index) => (
                  <tr key={`${record.date}-${index}`}>
                    <td>{record.date}</td>
                    <td>
                      <span
                        className={`student-status ${
                          record.status?.toLowerCase() === "present"
                            ? "status-present"
                            : "status-absent"
                        }`}
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
      </section>

      {/* Marks */}
      <section className="student-section">
        <div className="student-section-heading">
          <div>
            <h2>My Marks & Report Card</h2>
            <p>Your examination performance</p>
          </div>
          <span className="student-count">
            {marks.length} Results
          </span>
        </div>

        {marks.length === 0 ? (
          <div className="student-empty">
            No examination marks available.
          </div>
        ) : (
          <div className="student-table-wrapper">
            <table className="student-table">
              <thead>
                <tr>
                  <th>Examination</th>
                  <th>Exam Date</th>
                  <th>Subject</th>
                  <th>Obtained</th>
                  <th>Maximum</th>
                  <th>Percentage</th>
                </tr>
              </thead>

              <tbody>
                {marks.map((record, index) => {
                  const percentage =
                    Number(record.max_marks) > 0
                      ? (Number(record.marks_obtained) /
                          Number(record.max_marks)) *
                        100
                      : null;

                  return (
                    <tr
                      key={`${record.exam_name}-${record.subject}-${index}`}
                    >
                      <td>{record.exam_name}</td>
                      <td>{record.exam_date}</td>
                      <td>{record.subject}</td>
                      <td>{record.marks_obtained}</td>
                      <td>{record.max_marks}</td>
                      <td>
                        {percentage !== null
                          ? `${percentage.toFixed(2)}%`
                          : "N/A"}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Fees */}
      <section className="student-section">
        <div className="student-section-heading">
          <div>
            <h2>My Fees</h2>
            <p>Your fee payment information</p>
          </div>
        </div>

        {fees.length === 0 ? (
          <div className="student-empty">
            No fee records available.
          </div>
        ) : (
          <>
            <div className="student-fee-summary">
              <div>
                <span>Total Fees</span>
                <strong>{formatCurrency(totalFees)}</strong>
              </div>

              <div>
                <span>Paid Amount</span>
                <strong className="student-paid">
                  {formatCurrency(paidFees)}
                </strong>
              </div>

              <div>
                <span>Pending Amount</span>
                <strong className="student-pending">
                  {formatCurrency(pendingFees)}
                </strong>
              </div>
            </div>

            <div className="student-table-wrapper">
              <table className="student-table">
                <thead>
                  <tr>
                    <th>Total Fees</th>
                    <th>Paid Amount</th>
                    <th>Pending Amount</th>
                    <th>Payment Status</th>
                  </tr>
                </thead>

                <tbody>
                  {fees.map((fee, index) => (
                    <tr key={index}>
                      <td>{formatCurrency(fee.total_fee)}</td>
                      <td>{formatCurrency(fee.paid_amount)}</td>
                      <td>{formatCurrency(fee.pending_amount)}</td>
                      <td>
                        <span
                          className={`student-status ${
                            Number(fee.pending_amount) === 0
                              ? "status-present"
                              : "status-pending"
                          }`}
                        >
                          {Number(fee.pending_amount) === 0
                            ? "Fully Paid"
                            : "Payment Pending"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </section>
    </div>
  );
}

export default StudentDashboard;
