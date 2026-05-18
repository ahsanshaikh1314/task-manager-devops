const API_URL = '/api/tasks';

document.addEventListener('DOMContentLoaded', () => {
    loadTasks();
    document.getElementById('taskForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await addTask();
    });
});

async function loadTasks() {
    try {
        const response = await fetch(API_URL);
        const result = await response.json();
        const tasksList = document.getElementById('tasksList');
        if (result.success && result.data.length > 0) {
            tasksList.innerHTML = '';
            result.data.forEach(task => {
                tasksList.innerHTML += createTaskHTML(task);
            });
        } else {
            tasksList.innerHTML = '<p class="no-tasks">No tasks yet. Add your first task above!</p>';
        }
    } catch (error) {
        console.error('Error loading tasks:', error);
        document.getElementById('tasksList').innerHTML =
            '<p class="loading">⚠️ Error loading tasks. Please check if the server is running.</p>';
    }
}

async function addTask() {
    const title = document.getElementById('taskTitle').value;
    const description = document.getElementById('taskDescription').value;
    if (!title.trim()) { alert('⚠️ Please enter a task title'); return; }
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, description })
        });
        const result = await response.json();
        if (result.success) {
            document.getElementById('taskTitle').value = '';
            document.getElementById('taskDescription').value = '';
            await loadTasks();
        } else {
            alert('❌ Error adding task: ' + result.error);
        }
    } catch (error) {
        alert('❌ Error adding task. Please try again.');
    }
}

async function toggleTask(id, completed) {
    try {
        const response = await fetch(`${API_URL}/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ completed: !completed })
        });
        const result = await response.json();
        if (result.success) await loadTasks();
        else alert('❌ Error updating task: ' + result.error);
    } catch (error) {
        alert('❌ Error updating task. Please try again.');
    }
}

async function deleteTask(id) {
    if (!confirm('⚠️ Are you sure you want to delete this task?')) return;
    try {
        const response = await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        const result = await response.json();
        if (result.success) await loadTasks();
        else alert('❌ Error deleting task: ' + result.error);
    } catch (error) {
        alert('❌ Error deleting task. Please try again.');
    }
}

function createTaskHTML(task) {
    const date = new Date(task.createdAt).toLocaleDateString('en-US', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
    return `
        <div class="task-item ${task.completed ? 'completed' : ''}">
            <div class="task-header">
                <div class="task-title">${escapeHtml(task.title)}</div>
            </div>
            ${task.description ? `<div class="task-description">${escapeHtml(task.description)}</div>` : ''}
            <div class="task-date">${date}</div>
            <div class="task-actions">
                <button class="btn btn-complete" onclick="toggleTask('${task._id}', ${task.completed})">
                    ${task.completed ? '↩️ Undo' : '✅ Complete'}
                </button>
                <button class="btn btn-delete" onclick="deleteTask('${task._id}')">
                    🗑️ Delete
                </button>
            </div>
        </div>`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
