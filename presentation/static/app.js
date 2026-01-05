const API_URL = '/api';
let currentToken = null;
let currentUsername = null;
let allTasks = [];
let currentFilter = 'all';
let currentCategory = 'all';
let currentSort = 'position';
let editingTaskId = null;
let subtaskTaskId = null;
let draggedElement = null;

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    loadTheme();
});

function checkAuth() {
    currentToken = localStorage.getItem('token');
    currentUsername = localStorage.getItem('username');
    
    if (currentToken && currentUsername) {
        showApp();
    } else {
        showAuthScreen();
    }
}

function showAuthScreen() {
    document.getElementById('authScreen').style.display = 'flex';
    document.getElementById('appScreen').style.display = 'none';
}

function showApp() {
    document.getElementById('authScreen').style.display = 'none';
    document.getElementById('appScreen').style.display = 'flex';
    document.getElementById('usernameDisplay').textContent = currentUsername;
    
    loadTasks();
    
    document.getElementById('taskInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addTask();
        }
    });
    
    document.getElementById('subtaskInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            addSubtask();
        }
    });
}

function showLogin() {
    document.getElementById('loginTab').classList.add('active');
    document.getElementById('registerTab').classList.remove('active');
    document.getElementById('loginForm').style.display = 'flex';
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('loginError').textContent = '';
    document.getElementById('registerError').textContent = '';
}

function showRegister() {
    document.getElementById('registerTab').classList.add('active');
    document.getElementById('loginTab').classList.remove('active');
    document.getElementById('registerForm').style.display = 'flex';
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('loginError').textContent = '';
    document.getElementById('registerError').textContent = '';
}

async function register() {
    const username = document.getElementById('registerUsername').value.trim();
    const email = document.getElementById('registerEmail').value.trim();
    const password = document.getElementById('registerPassword').value;
    const errorDiv = document.getElementById('registerError');
    
    errorDiv.textContent = '';
    
    if (!username || !email || !password) {
        errorDiv.textContent = 'All fields are required';
        return;
    }
    
    if (username.length < 3) {
        errorDiv.textContent = 'Username must be at least 3 characters';
        return;
    }
    
    if (password.length < 6) {
        errorDiv.textContent = 'Password must be at least 6 characters';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });
        
        if (response.ok) {
            alert('Registration successful! Please login.');
            showLogin();
        } else {
            const data = await response.json();
            errorDiv.textContent = data.detail || 'Registration failed';
        }
    } catch (error) {
        console.error('Error:', error);
        errorDiv.textContent = 'Network error. Please try again.';
    }
}

async function login() {
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value;
    const errorDiv = document.getElementById('loginError');
    
    errorDiv.textContent = '';
    
    if (!username || !password) {
        errorDiv.textContent = 'Both fields are required';
        return;
    }
    
    try {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData
        });
        
        if (response.ok) {
            const data = await response.json();
            currentToken = data.access_token;
            currentUsername = username;
            
            localStorage.setItem('token', currentToken);
            localStorage.setItem('username', currentUsername);
            
            showApp();
        } else {
            const data = await response.json();
            errorDiv.textContent = data.detail || 'Login failed';
        }
    } catch (error) {
        console.error('Error:', error);
        errorDiv.textContent = 'Network error. Please try again.';
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    currentToken = null;
    currentUsername = null;
    allTasks = [];
    showAuthScreen();
}

function loadTheme() {
    const theme = localStorage.getItem('theme') || 'light';
    if (theme === 'dark') {
        document.body.classList.add('dark-theme');
        document.querySelector('.theme-icon').textContent = '☀️';
    }
}

function toggleTheme() {
    document.body.classList.toggle('dark-theme');
    const isDark = document.body.classList.contains('dark-theme');
    document.querySelector('.theme-icon').textContent = isDark ? '☀️' : '🌙';
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

async function loadTasks() {
    try {
        const response = await fetch(`${API_URL}/tasks/`, {
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        allTasks = await response.json();
        updateStats();
        updateExtendedStats();
        applySorting();
    } catch (error) {
        console.error('Error loading tasks:', error);
        alert('Failed to load tasks');
    }
}

function updateStats() {
    const total = allTasks.length;
    const completed = allTasks.filter(t => t.completed).length;
    const active = total - completed;
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    document.getElementById('totalTasks').textContent = total;
    document.getElementById('activeTasks').textContent = active;
    document.getElementById('completedTasks').textContent = completed;
    document.getElementById('progressFill').style.width = percentage + '%';
    document.getElementById('progressText').textContent = percentage + '%';
}

function updateExtendedStats() {
    const now = new Date();
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const oneMonthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    
    const completedThisWeek = allTasks.filter(t => {
        if (!t.completed || !t.created_at) return false;
        const createdDate = new Date(t.created_at);
        return createdDate >= oneWeekAgo;
    }).length;
    
    const completedThisMonth = allTasks.filter(t => {
        if (!t.completed || !t.created_at) return false;
        const createdDate = new Date(t.created_at);
        return createdDate >= oneMonthAgo;
    }).length;
    
    const overdueTasks = allTasks.filter(t => {
        if (t.completed || !t.deadline) return false;
        return new Date(t.deadline) < now;
    }).length;
    
    document.getElementById('thisWeek').textContent = completedThisWeek;
    document.getElementById('thisMonth').textContent = completedThisMonth;
    document.getElementById('overdue').textContent = overdueTasks;
}

function setFilter(filter) {
    currentFilter = filter;
    
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
    
    filterTasks();
}

function setCategory(category) {
    currentCategory = category;
    
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.querySelector(`[data-category="${category}"]`).classList.add('active');
    
    filterTasks();
}

function applySorting() {
    currentSort = document.getElementById('sortSelect').value;
    
    let sortedTasks = [...allTasks];
    
    switch(currentSort) {
        case 'deadline':
            sortedTasks.sort((a, b) => {
                if (!a.deadline) return 1;
                if (!b.deadline) return -1;
                return new Date(a.deadline) - new Date(b.deadline);
            });
            break;
        case 'priority':
            const priorityOrder = { high: 0, medium: 1, low: 2 };
            sortedTasks.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
            break;
        case 'status':
            sortedTasks.sort((a, b) => a.completed - b.completed);
            break;
        case 'created':
            sortedTasks.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            break;
        case 'position':
        default:
            sortedTasks.sort((a, b) => a.position - b.position);
            break;
    }
    
    allTasks = sortedTasks;
    filterTasks();
}

function filterTasks() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase().trim();
    
    let filteredTasks = allTasks;
    
    if (currentFilter === 'active') {
        filteredTasks = filteredTasks.filter(t => !t.completed);
    } else if (currentFilter === 'completed') {
        filteredTasks = filteredTasks.filter(t => t.completed);
    }
    
    if (currentCategory !== 'all') {
        filteredTasks = filteredTasks.filter(t => t.category === currentCategory);
    }
    
    if (searchTerm) {
        filteredTasks = filteredTasks.filter(t => 
            t.title.toLowerCase().includes(searchTerm)
        );
    }
    
    displayTasks(filteredTasks);
}

function displayTasks(tasks) {
    const taskList = document.getElementById('taskList');
    const emptyMessage = document.getElementById('emptyMessage');
    
    taskList.innerHTML = '';
    
    if (tasks.length === 0) {
        emptyMessage.classList.add('show');
        return;
    }
    
    emptyMessage.classList.remove('show');
    
    tasks.forEach(task => {
        const taskItem = createTaskElement(task);
        taskList.appendChild(taskItem);
    });
}

function createTaskElement(task) {
    const div = document.createElement('div');
    div.className = `task-item priority-${task.priority}`;
    div.draggable = currentSort === 'position';
    div.dataset.taskId = task.id;
    
    if (task.completed) {
        div.classList.add('completed');
    }
    
    const now = new Date();
    const isOverdue = task.deadline && new Date(task.deadline) < now && !task.completed;
    
    if (isOverdue) {
        div.classList.add('overdue');
    }
    
    let deadlineHtml = '';
    if (task.deadline) {
        const deadlineDate = new Date(task.deadline);
        const formatted = formatDeadline(deadlineDate);
        const overdueCls = isOverdue ? 'overdue' : '';
        deadlineHtml = `<span class="task-deadline ${overdueCls}">📅 ${formatted}</span>`;
    }
    
    let categoryHtml = '';
    if (task.category) {
        const categoryIcons = {
            work: '💼',
            personal: '🏠',
            study: '📚',
            sport: '⚽'
        };
        categoryHtml = `<span class="task-category ${task.category}">${categoryIcons[task.category]} ${task.category}</span>`;
    }
    
    let priorityHtml = `<span class="task-priority priority-${task.priority}">${task.priority}</span>`;
    
    let subtasksHtml = '';
    if (task.subtasks && task.subtasks.length > 0) {
        const completedSubtasks = task.subtasks.filter(s => s.completed).length;
        const totalSubtasks = task.subtasks.length;
        subtasksHtml = `<span class="subtask-progress">${completedSubtasks}/${totalSubtasks} subtasks</span>`;
        
        const subtaskItems = task.subtasks.map(subtask => `
            <div class="subtask-item ${subtask.completed ? 'completed' : ''}">
                <input 
                    type="checkbox" 
                    ${subtask.completed ? 'checked' : ''} 
                    onchange="toggleSubtaskInline(${task.id}, ${subtask.id}, ${!subtask.completed})"
                >
                <span class="subtask-title">${escapeHtml(subtask.title)}</span>
                <button class="subtask-delete" onclick="deleteSubtaskInline(${task.id}, ${subtask.id})">×</button>
            </div>
        `).join('');
        
        if (subtaskItems) {
            subtasksHtml += `<div class="task-subtasks">${subtaskItems}</div>`;
        }
    }
    
    div.innerHTML = `
        <div class="task-main">
            <input 
                type="checkbox" 
                ${task.completed ? 'checked' : ''} 
                onchange="toggleTask(${task.id}, ${!task.completed})"
            >
            <div class="task-content">
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-meta">
                    ${priorityHtml}
                    ${categoryHtml}
                    ${deadlineHtml}
                    ${subtasksHtml.includes('subtask-progress') ? subtasksHtml.split('</div>')[0] + '</div>' : ''}
                </div>
            </div>
            <div class="task-actions">
                <button class="edit-btn" onclick="openEditModal(${task.id})">Edit</button>
                <button class="subtask-btn" onclick="openSubtaskModal(${task.id})">Subtasks</button>
                <button class="delete-btn" onclick="deleteTask(${task.id})">Delete</button>
            </div>
        </div>
        ${task.subtasks && task.subtasks.length > 0 ? subtasksHtml.split('subtask-progress">')[1] || '' : ''}
    `;
    
    if (currentSort === 'position') {
        div.addEventListener('dragstart', handleDragStart);
        div.addEventListener('dragend', handleDragEnd);
        div.addEventListener('dragover', handleDragOver);
        div.addEventListener('drop', handleDrop);
        div.addEventListener('dragleave', handleDragLeave);
    }
    
    return div;
}

function handleDragStart(e) {
    draggedElement = e.target;
    e.target.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
    document.querySelectorAll('.task-item').forEach(item => {
        item.classList.remove('drag-over');
    });
    draggedElement = null;
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    
    const target = e.target.closest('.task-item');
    if (target && target !== draggedElement) {
        target.classList.add('drag-over');
    }
    
    return false;
}

function handleDragLeave(e) {
    const target = e.target.closest('.task-item');
    if (target) {
        target.classList.remove('drag-over');
    }
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    const target = e.target.closest('.task-item');
    if (draggedElement !== target && target) {
        const taskList = document.getElementById('taskList');
        const allItems = [...taskList.children];
        const draggedIndex = allItems.indexOf(draggedElement);
        const targetIndex = allItems.indexOf(target);
        
        if (draggedIndex < targetIndex) {
            target.parentNode.insertBefore(draggedElement, target.nextSibling);
        } else {
            target.parentNode.insertBefore(draggedElement, target);
        }
        
        saveTaskPositions();
    }
    
    target.classList.remove('drag-over');
    return false;
}

async function saveTaskPositions() {
    const taskList = document.getElementById('taskList');
    const items = [...taskList.children];
    const positions = {};
    
    items.forEach((item, index) => {
        const taskId = item.dataset.taskId;
        positions[taskId] = index;
    });
    
    try {
        await fetch(`${API_URL}/tasks/positions/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify(positions)
        });
        
        await loadTasks();
    } catch (error) {
        console.error('Error saving positions:', error);
    }
}

function formatDeadline(date) {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
}

async function addTask() {
    const input = document.getElementById('taskInput');
    const deadlineInput = document.getElementById('deadlineInput');
    const prioritySelect = document.getElementById('prioritySelect');
    const categorySelect = document.getElementById('categorySelect');
    
    const title = input.value.trim();
    const deadline = deadlineInput.value || null;
    const priority = prioritySelect.value;
    const category = categorySelect.value || null;
    
    if (!title) {
        alert('Please enter task title');
        return;
    }
    
    const taskData = { 
        title: title,
        priority: priority,
        category: category
    };
    
    if (deadline) {
        taskData.deadline = new Date(deadline).toISOString();
    }
    
    try {
        const response = await fetch(`${API_URL}/tasks/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify(taskData)
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok) {
            input.value = '';
            deadlineInput.value = '';
            prioritySelect.value = 'medium';
            categorySelect.value = '';
            await loadTasks();
        } else {
            alert('Error adding task');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to add task');
    }
}

async function toggleTask(taskId, completed) {
    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ completed: completed })
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok) {
            await loadTasks();
        } else {
            alert('Error updating task');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update task');
    }
}

async function deleteTask(taskId) {
    if (!confirm('Delete this task?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok || response.status === 204) {
            await loadTasks();
        } else {
            alert('Error deleting task');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete task');
    }
}

async function clearCompleted() {
    const completedCount = allTasks.filter(t => t.completed).length;
    
    if (completedCount === 0) {
        alert('No completed tasks to clear');
        return;
    }
    
    if (!confirm(`Delete ${completedCount} completed task(s)?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/tasks/completed/all`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok) {
            await loadTasks();
        } else {
            alert('Error clearing completed tasks');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to clear completed tasks');
    }
}

function openEditModal(taskId) {
    const task = allTasks.find(t => t.id === taskId);
    if (!task) return;
    
    editingTaskId = taskId;
    
    document.getElementById('editTaskInput').value = task.title;
    document.getElementById('editPrioritySelect').value = task.priority;
    document.getElementById('editCategorySelect').value = task.category || '';
    
    if (task.deadline) {
        const deadlineDate = new Date(task.deadline);
        const localDate = new Date(deadlineDate.getTime() - deadlineDate.getTimezoneOffset() * 60000);
        document.getElementById('editDeadlineInput').value = localDate.toISOString().slice(0, 16);
    } else {
        document.getElementById('editDeadlineInput').value = '';
    }
    
    document.getElementById('editModal').classList.add('show');
}

function closeEditModal() {
    document.getElementById('editModal').classList.remove('show');
    editingTaskId = null;
}

async function saveEdit() {
    const title = document.getElementById('editTaskInput').value.trim();
    const priority = document.getElementById('editPrioritySelect').value;
    const category = document.getElementById('editCategorySelect').value || null;
    const deadline = document.getElementById('editDeadlineInput').value || null;
    
    if (!title) {
        alert('Task title cannot be empty');
        return;
    }
    
    const updateData = {
        title: title,
        priority: priority,
        category: category
    };
    
    if (deadline) {
        updateData.deadline = new Date(deadline).toISOString();
    }
    
    try {
        const response = await fetch(`${API_URL}/tasks/${editingTaskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify(updateData)
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok) {
            closeEditModal();
            await loadTasks();
        } else {
            alert('Error updating task');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update task');
    }
}

function openSubtaskModal(taskId) {
    const task = allTasks.find(t => t.id === taskId);
    if (!task) return;
    
    subtaskTaskId = taskId;
    
    displaySubtasks(task.subtasks || []);
    
    document.getElementById('subtaskModal').classList.add('show');
}

function closeSubtaskModal() {
    document.getElementById('subtaskModal').classList.remove('show');
    document.getElementById('subtaskInput').value = '';
    subtaskTaskId = null;
}

function displaySubtasks(subtasks) {
    const subtaskList = document.getElementById('subtaskList');
    subtaskList.innerHTML = '';
    
    if (subtasks.length === 0) {
        subtaskList.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 20px;">No subtasks yet</p>';
        return;
    }
    
    subtasks.forEach(subtask => {
        const div = document.createElement('div');
        div.className = `subtask-item ${subtask.completed ? 'completed' : ''}`;
        div.innerHTML = `
            <input 
                type="checkbox" 
                ${subtask.completed ? 'checked' : ''} 
                onchange="toggleSubtaskModal(${subtask.id}, ${!subtask.completed})"
            >
            <span class="subtask-title">${escapeHtml(subtask.title)}</span>
            <button class="subtask-delete" onclick="deleteSubtaskModal(${subtask.id})">×</button>
        `;
        subtaskList.appendChild(div);
    });
}

async function addSubtask() {
    const input = document.getElementById('subtaskInput');
    const title = input.value.trim();
    
    if (!title) {
        alert('Please enter subtask title');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/tasks/${subtaskTaskId}/subtasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ title: title })
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok) {
            input.value = '';
            await loadTasks();
            const task = allTasks.find(t => t.id === subtaskTaskId);
            if (task) {
                displaySubtasks(task.subtasks || []);
            }
        } else {
            alert('Error adding subtask');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to add subtask');
    }
}

async function toggleSubtaskModal(subtaskId, completed) {
    try {
        const response = await fetch(`${API_URL}/tasks/${subtaskTaskId}/subtasks/${subtaskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ completed: completed })
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok) {
            await loadTasks();
            const task = allTasks.find(t => t.id === subtaskTaskId);
            if (task) {
                displaySubtasks(task.subtasks || []);
            }
        } else {
            alert('Error updating subtask');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update subtask');
    }
}

async function deleteSubtaskModal(subtaskId) {
    if (!confirm('Delete this subtask?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/tasks/${subtaskTaskId}/subtasks/${subtaskId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok || response.status === 204) {
            await loadTasks();
            const task = allTasks.find(t => t.id === subtaskTaskId);
            if (task) {
                displaySubtasks(task.subtasks || []);
            }
        } else {
            alert('Error deleting subtask');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete subtask');
    }
}

async function toggleSubtaskInline(taskId, subtaskId, completed) {
    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}/subtasks/${subtaskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${currentToken}`
            },
            body: JSON.stringify({ completed: completed })
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok) {
            await loadTasks();
        } else {
            alert('Error updating subtask');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to update subtask');
    }
}

async function deleteSubtaskInline(taskId, subtaskId) {
    if (!confirm('Delete this subtask?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/tasks/${taskId}/subtasks/${subtaskId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${currentToken}`
            }
        });
        
        if (response.status === 401) {
            logout();
            return;
        }
        
        if (response.ok || response.status === 204) {
            await loadTasks();
        } else {
            alert('Error deleting subtask');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to delete subtask');
    }
}

document.addEventListener('click', (e) => {
    const editModal = document.getElementById('editModal');
    const subtaskModal = document.getElementById('subtaskModal');
    
    if (e.target === editModal) {
        closeEditModal();
    }
    
    if (e.target === subtaskModal) {
        closeSubtaskModal();
    }
});

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
