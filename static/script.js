/**
 * Dashboard Client-Side Logic
 * Handles dynamic chart loading, Excel table interactions, and batch editing.
 */

// --- Global State ---
let pendingChanges = {}; // Stores batch edits: { rowIndex: { columnName: newValue } }

// --- Dashboard & Chart Loading ---

/**
 * Loads a chart or Excel table into the central workspace.
 * @param {string} chartId - The unique identifier for the report.
 */
function showChart(chartId) {
    const workspace = document.getElementById('chart-workspace');
    if (!workspace) return;
    
    // Reset state for new view
    pendingChanges = {}; 

    // Show loading state
    workspace.innerHTML = `
        <div class="loading-spinner"></div>
        <span class="loading-text">Generating data...</span>
    `; 

    // Handle Excel table reports
    if (chartId.includes('excel')) {
        fetch(`/${chartId}?t=${new Date().getTime()}`)
            .then(response => response.text())
            .then(html => {
                workspace.innerHTML = `<div class="table-wrapper">${html}</div>`;
                
                // Create and append the batch save button (initially hidden)
                const saveBtn = document.createElement('button');
                saveBtn.id = 'save-excel-btn';
                saveBtn.className = 'dynamic-chart-btn save-btn';
                saveBtn.style.display = 'none'; 
                saveBtn.textContent = 'Save Changes';
                saveBtn.onclick = () => saveExcelChanges(chartId === 'show-excel-full', workspace);
                workspace.appendChild(saveBtn);

                // Initialize interactive features
                makeTableEditable(workspace);
            })
            .catch(err => {
                renderError(workspace, `Failed to load data: ${err}`);
            });
    } 
    // Handle Image-based chart reports
    else {
        const img = document.createElement("img");
        img.src = `/${chartId}?t=${new Date().getTime()}`;
        img.alt = chartId;
        img.onload = () => {
            workspace.innerHTML = "";
            workspace.appendChild(img);
        };
        img.onerror = () => {
            renderError(workspace, "Failed to generate chart image");
        };
    }
}

/**
 * Clears the active workspace and resets pending changes.
 */
function clearCharts() {
    const workspace = document.getElementById('chart-workspace');
    if (workspace) {
        workspace.innerHTML = '';
        pendingChanges = {};
    }
}

// --- Table Interaction Logic ---

/**
 * Initializes a table for editing and sorting.
 * @param {HTMLElement} container - The container holding the table.
 */
function makeTableEditable(container) {
    const table = container.querySelector('table');
    if (!table) return;

    const headers = Array.from(table.querySelectorAll('thead th'));
    const rows = Array.from(table.querySelectorAll('tbody tr'));

    // Attach sorting listeners to headers
    headers.forEach((th, index) => {
        th.onclick = () => sortTable(table, index);
    });

    // Initialize each row for editing
    rows.forEach(row => {
        const rowIndex = row.querySelector('th').textContent.trim(); // First th is the index
        const cells = row.querySelectorAll('td');

        cells.forEach((cell, cellIndex) => {
            // cellIndex matches the index in headers (ignoring the index th)
            const columnName = headers[cellIndex + 1].textContent.trim(); 
            const originalValue = cell.textContent.trim();
            
            cell.contentEditable = true;
            cell.classList.add('editable-cell');
            
            // Handle real-time input and validation
            cell.oninput = () => {
                const newValue = cell.textContent.trim();
                let isValid = true;

                // Column-specific validation
                if (columnName === 'Revenue') {
                    if (newValue !== '' && isNaN(parseFloat(newValue))) {
                        isValid = false;
                        cell.classList.add('cell-error');
                    } else {
                        cell.classList.remove('cell-error');
                    }
                } else if (columnName === 'Date') {
                    const dateTest = new Date(newValue);
                    if (newValue !== '' && isNaN(dateTest.getTime())) {
                        isValid = false;
                        cell.classList.add('cell-error');
                        showSnackbar('Invalid date format. Use YYYY-MM-DD.', 'error');
                    } else {
                        cell.classList.remove('cell-error');
                    }
                }

                // Track changes if valid
                if (isValid && newValue !== originalValue) {
                    if (!pendingChanges[rowIndex]) pendingChanges[rowIndex] = {};
                    pendingChanges[rowIndex][columnName] = newValue;
                    cell.classList.add('cell-changed');
                } else {
                    if (pendingChanges[rowIndex]) delete pendingChanges[rowIndex][columnName];
                    if (pendingChanges[rowIndex] && Object.keys(pendingChanges[rowIndex]).length === 0) delete pendingChanges[rowIndex];
                    cell.classList.remove('cell-changed');
                }

                // Update Save button visibility
                const saveBtn = document.getElementById('save-excel-btn');
                const hasErrors = container.querySelectorAll('.cell-error').length > 0;
                if (saveBtn) {
                    saveBtn.style.display = (Object.keys(pendingChanges).length > 0 && !hasErrors) ? 'block' : 'none';
                }
            };
            
            // Save on Enter key
            cell.onkeypress = (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    cell.blur();
                }
            };
        });
    });
}

/**
 * Sorts the table by a specific column.
 * @param {HTMLTableElement} table 
 * @param {number} colIndex 
 */
function sortTable(table, colIndex) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const headers = table.querySelectorAll('thead th');
    const th = headers[colIndex];
    const columnName = th.textContent.trim().toLowerCase();
    const isAscending = th.classList.contains('sort-asc');
    
    // UI: Clear other headers and toggle current one
    headers.forEach(header => {
        if (header !== th) header.classList.remove('sort-asc', 'sort-desc');
    });
    th.classList.toggle('sort-asc', !isAscending);
    th.classList.toggle('sort-desc', isAscending);

    const direction = isAscending ? -1 : 1;

    // Sorting logic
    const sortedRows = rows.sort((a, b) => {
        let valA, valB;
        
        // Handle th (index) and td (data) cells
        if (colIndex === 0) {
            valA = a.querySelector('th').textContent.trim();
            valB = b.querySelector('th').textContent.trim();
        } else {
            valA = a.querySelectorAll('td')[colIndex - 1].textContent.trim();
            valB = b.querySelectorAll('td')[colIndex - 1].textContent.trim();
        }

        // 1. Date sorting
        if (columnName === 'date') {
            const dateA = new Date(valA);
            const dateB = new Date(valB);
            if (!isNaN(dateA) && !isNaN(dateB)) return (dateA - dateB) * direction;
        }

        // 2. Numeric sorting
        const numA = parseFloat(valA.replace(/[$,]/g, ''));
        const numB = parseFloat(valB.replace(/[$,]/g, ''));
        if (!isNaN(numA) && !isNaN(numB)) return (numA - numB) * direction;

        // 3. String sorting (fallback)
        return valA.localeCompare(valB) * direction;
    });

    // Re-append rows in new order
    sortedRows.forEach(row => tbody.appendChild(row));
}

// --- Data Saving Logic ---

/**
 * Sends batch changes to the server.
 * @param {boolean} isFull - Whether the full table view is active.
 * @param {HTMLElement} container - The table container.
 */
function saveExcelChanges(isFull, container) {
    const saveBtn = document.getElementById('save-excel-btn');
    if (saveBtn) {
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
    }

    fetch('/edit-excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            changes: pendingChanges,
            fetch_full: isFull
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSnackbar('Changes saved successfully!', 'success');
            pendingChanges = {}; 

            // Update Global Stats
            const totalRevEl = document.getElementById('total-revenue-value');
            if (totalRevEl && data.total_revenue !== undefined) {
                totalRevEl.textContent = `$${data.total_revenue}`;
            }

            // Refresh table with updated data
            container.innerHTML = `<div class="table-wrapper">${data.html}</div>`;
            
            // Re-append save button and re-init listeners
            const newSaveBtn = document.createElement('button');
            newSaveBtn.id = 'save-excel-btn';
            newSaveBtn.className = 'dynamic-chart-btn save-btn';
            newSaveBtn.style.display = 'none';
            newSaveBtn.textContent = 'Save Changes';
            newSaveBtn.onclick = () => saveExcelChanges(isFull, container);
            container.appendChild(newSaveBtn);
            
            makeTableEditable(container);
        } else {
            showSnackbar(`Error saving changes: ${data.error}`, 'error');
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.textContent = 'Save Changes';
            }
        }
    })
    .catch(error => {
        showSnackbar('Network error while saving changes', 'error');
        if (saveBtn) {
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save Changes';
        }
    });
}

// --- UI Utility Functions ---

/**
 * Displays a temporary snackbar notification.
 * @param {string} message 
 * @param {string} type - 'success', 'error', or 'info'
 */
function showSnackbar(message, type = 'info') {
    const snackbar = document.getElementById('snackbar');
    if (!snackbar) return;
    
    snackbar.textContent = message;
    snackbar.className = `show ${type}`;
    
    setTimeout(() => {
        snackbar.className = snackbar.className.replace('show', '');
    }, 3000);
}

/**
 * Renders an error message in the workspace.
 */
function renderError(container, message) {
    container.innerHTML = `
        <div style="color: var(--danger-color); text-align: center;">
            <p style="font-weight: 700; margin-bottom: 0.5rem;">System Error</p>
            <p style="font-size: 0.875rem;">${message}</p>
        </div>
    `;
}

console.log("script.js loaded successfully!");
