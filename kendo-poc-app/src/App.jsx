import { useState } from "react";
import { Grid, GridColumn } from "@progress/kendo-react-grid";
import { DropDownList } from "@progress/kendo-react-dropdowns";
import { Input, NumericTextBox } from "@progress/kendo-react-inputs";
import { Button } from "@progress/kendo-react-buttons";
import { DatePicker } from "@progress/kendo-react-dateinputs";
import "@progress/kendo-theme-default/dist/all.css";

const gridData = [
    { id: 1, name: "Alice Johnson", role: "Admin", status: "Active", joinDate: new Date("2022-01-15") },
    { id: 2, name: "Bob Smith", role: "User", status: "Inactive", joinDate: new Date("2021-06-20") },
    { id: 3, name: "Carol White", role: "Manager", status: "Active", joinDate: new Date("2023-03-10") },
    { id: 4, name: "David Lee", role: "User", status: "Pending", joinDate: new Date("2024-01-05") },
];

const roles = ["Admin", "Manager", "User", "Guest"];
const statusOptions = ["Active", "Inactive", "Pending"];

export default function App() {
    const [selectedRole, setSelectedRole] = useState(roles[0]);
    const [selectedStatus, setSelectedStatus] = useState(statusOptions[0]);
    const [searchText, setSearchText] = useState("");
    const [age, setAge] = useState(25);
    const [selectedDate, setSelectedDate] = useState(new Date());
    const [formSubmitted, setFormSubmitted] = useState(false);
    const [filterData, setFilterData] = useState(gridData);

    const handleSearch = () => {
        const filtered = gridData.filter((d) =>
            d.name.toLowerCase().includes(searchText.toLowerCase())
        );
        setFilterData(filtered);
        setFormSubmitted(false);
    };

    const handleSubmit = () => setFormSubmitted(true);

    const handleReset = () => {
        setSearchText("");
        setSelectedRole(roles[0]);
        setSelectedStatus(statusOptions[0]);
        setAge(25);
        setSelectedDate(new Date());
        setFilterData(gridData);
        setFormSubmitted(false);
    };

    return (
        <div style={styles.page}>
            <header style={styles.header}>
                <h1 style={styles.title}>KendoReact PoC - Dynamic Locator Testing</h1>
                <p style={styles.subtitle}>Selenium-Python Dynamic Locator Fix Playground</p>
            </header>

            <main style={styles.main}>
                <section style={styles.card} className="userForm">
                    <h2 style={styles.sectionTitle}>User Input Form</h2>
                    <div style={styles.formGrid}>

                        <div style={styles.field}>
                            <label style={styles.label}>Search Name</label>
                            <Input
                                id="searchBox"
                                placeholder="Enter name..."
                                value={searchText}
                                onChange={(e) => setSearchText(e.value)}
                                style={styles.inputFull}
                            />
                        </div>

                        <div style={styles.field}>
                            <label style={styles.label}>Select Role</label>
                            <DropDownList
                                id="RoleDropDown"
                                data={roles}
                                value={selectedRole}
                                onChange={(e) => setSelectedRole(e.value)}
                                style={styles.inputFull}
                            />
                        </div>

                        <div style={styles.field}>
                            <label style={styles.label}>Select Status</label>
                            <DropDownList
                                data={statusOptions}
                                value={selectedStatus}
                                onChange={(e) => setSelectedStatus(e.value)}
                                style={styles.inputFull}
                            />
                        </div>

                        <div style={styles.field}>
                            <label style={styles.label}>Age</label>
                            <NumericTextBox
                                id="ageInput"
                                value={age}
                                min={1}
                                max={120}
                                onChange={(e) => setAge(e.value)}
                                style={styles.inputFull}
                            />
                        </div>

                        <div style={styles.field}>
                            <label style={styles.label}>Join Date</label>
                            <DatePicker
                                value={selectedDate}
                                onChange={(e) => setSelectedDate(e.value)}
                                style={styles.inputFull}
                            />
                        </div>

                    </div>

                    <div style={styles.buttonRow}>
                        <Button themeColor="primary" onClick={handleSearch} style={styles.btn}>Search</Button>
                        <Button themeColor="success" onClick={handleSubmit} style={styles.btn}>Submit</Button>
                        <Button themeColor="error" onClick={handleReset} style={styles.btn}>Reset</Button>
                    </div>

                    {formSubmitted && (
                        <div style={styles.successBanner}>
                            Submitted! Role: <strong>{selectedRole}</strong> | Status: <strong>{selectedStatus}</strong> | Age: <strong>{age}</strong>
                        </div>
                    )}
                </section>

                <section style={styles.card}>
                    <h2 style={styles.sectionTitle}>User Data Grid</h2>
                    <Grid
                        className="userDataGrid"
                        data={filterData}
                        style={{ height: "260px" }}
                    >
                        <GridColumn field="id" title="ID" width="60px" />
                        <GridColumn field="name" title="Full Name" />
                        <GridColumn field="role" title="Role" />
                        <GridColumn field="status" title="Status" />
                        <GridColumn field="joinDate" title="Join Date" format="{0:MM/dd/yyyy}" />
                    </Grid>
                    <span style={styles.gridCaption}>
                        Showing {filterData.length} of {gridData.length} records
                    </span>
                </section>
            </main>

            <footer style={styles.footer}>
                KendoReact PoC - Dynamic Locator Testing - Selenium-Python
            </footer>
        </div>
    );
}

const styles = {
    page: { fontFamily: "'Segoe UI', sans-serif", background: "#f0f4f8", minHeight: "100vh", margin: 0 },
    header: { background: "linear-gradient(135deg, #1e3a5f, #2e6da4)", color: "#fff", padding: "32px 40px" },
    title: { margin: 0, fontSize: "26px", fontWeight: 700 },
    subtitle: { margin: "8px 0 0", fontSize: "14px", opacity: 0.8 },
    main: { maxWidth: "1100px", margin: "32px auto", padding: "0 20px", display: "flex", flexDirection: "column", gap: "24px" },
    card: { background: "#fff", borderRadius: "10px", padding: "28px 32px", boxShadow: "0 2px 10px rgba(0,0,0,0.08)" },
    sectionTitle: { margin: "0 0 20px", fontSize: "18px", fontWeight: 600, color: "#1e3a5f", borderBottom: "2px solid #2e6da4", paddingBottom: "8px" },
    formGrid: { display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "20px", marginBottom: "20px" },
    field: { display: "flex", flexDirection: "column", gap: "6px" },
    label: { fontSize: "13px", fontWeight: 600, color: "#444" },
    inputFull: { width: "100%" },
    buttonRow: { display: "flex", gap: "12px", flexWrap: "wrap" },
    btn: { minWidth: "120px" },
    successBanner: { marginTop: "16px", background: "#e6f4ea", border: "1px solid #4caf50", borderRadius: "6px", padding: "12px 16px", color: "#2e7d32", fontSize: "14px" },
    gridCaption: { marginTop: "10px", fontSize: "13px", color: "#666", display: "block", textAlign: "right" },
    footer: { textAlign: "center", padding: "20px", fontSize: "12px", color: "#888" },
};