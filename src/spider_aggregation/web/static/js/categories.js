// MindWeaver - Category Management JavaScript

// ============================================================================
// Category Form Handling
// ============================================================================

function showAddCategoryModal() {
    const content = `
        <form id="category-form" onsubmit="handleCategorySubmit(event)">
            <div class="form-group">
                <label for="category-name">分类名称 *</label>
                <input type="text" id="category-name" name="name" class="form-control" required placeholder="技术博客">
                <div class="form-help">分类名称必须唯一</div>
            </div>

            <div class="form-group">
                <label for="category-description">描述</label>
                <textarea id="category-description" name="description" class="form-control" rows="2" placeholder="关于技术、编程相关的文章"></textarea>
            </div>

            <div class="form-group">
                <label for="category-color">颜色</label>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <input type="color" id="category-color" name="color" class="form-control" value="#3b82f6" style="width: 60px; height: 40px; padding: 0.25rem;">
                    <div class="form-help" style="margin-bottom: 0;">选择分类标识颜色</div>
                </div>
            </div>

            <div class="form-group">
                <label for="category-icon">图标</label>
                <input type="text" id="category-icon" name="icon" class="form-control" placeholder="📁" maxlength="2" style="width: 100px;">
                <div class="form-help">使用 emoji 作为图标（可选）</div>
            </div>

            <div class="form-group">
                <label>
                    <input type="checkbox" name="enabled" checked>
                    启用此分类
                </label>
            </div>

            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="App.modal.hide()">取消</button>
                <button type="submit" class="btn btn-primary">创建分类</button>
            </div>
        </form>
    `;

    App.modal.show('添加分类', content);
}

function showEditCategoryModal(categoryId) {
    const categoryData = window.categoryData.find(c => c.id === categoryId);
    if (!categoryData) {
        App.showToast('未找到分类', 'error');
        return;
    }

    const content = `
        <form id="category-form" onsubmit="handleCategoryUpdate(event, ${categoryId})">
            <div class="form-group">
                <label for="category-name">分类名称 *</label>
                <input type="text" id="category-name" name="name" class="form-control" required value="${App.escapeHtml(categoryData.name)}">
            </div>

            <div class="form-group">
                <label for="category-description">描述</label>
                <textarea id="category-description" name="description" class="form-control" rows="2">${App.escapeHtml(categoryData.description || '')}</textarea>
            </div>

            <div class="form-group">
                <label for="category-color">颜色</label>
                <div style="display: flex; gap: 0.5rem; align-items: center;">
                    <input type="color" id="category-color" name="color" class="form-control" value="${categoryData.color || '#3b82f6'}" style="width: 60px; height: 40px; padding: 0.25rem;">
                </div>
            </div>

            <div class="form-group">
                <label for="category-icon">图标</label>
                <input type="text" id="category-icon" name="icon" class="form-control" value="${App.escapeHtml(categoryData.icon || '')}" placeholder="📁" maxlength="2" style="width: 100px;">
            </div>

            <div class="form-group">
                <label>
                    <input type="checkbox" name="enabled" ${categoryData.enabled ? 'checked' : ''}>
                    启用此分类
                </label>
            </div>

            <div class="form-actions">
                <button type="button" class="btn btn-secondary" onclick="App.modal.hide()">取消</button>
                <button type="submit" class="btn btn-primary">更新分类</button>
            </div>
        </form>
    `;

    App.modal.show('编辑分类', content);
}

async function handleCategorySubmit(event) {
    event.preventDefault();
    const form = event.target;
    const validation = App.form.validate(form);

    if (!validation.valid) {
        App.showToast('请修正表单中的错误', 'error');
        return;
    }

    const data = App.form.serialize(form);

    try {
        const response = await App.api.post('/api/categories', data);

        if (response.success) {
            App.showToast('分类创建成功', 'success');
            App.modal.hide();
            setTimeout(() => location.reload(), 500);
        } else {
            App.showToast(response.error || '创建分类失败', 'error');
        }
    } catch (error) {
        console.error('创建分类错误:', error);
        App.showToast('创建分类失败', 'error');
    }
}

async function handleCategoryUpdate(event, categoryId) {
    event.preventDefault();
    const form = event.target;
    const validation = App.form.validate(form);

    if (!validation.valid) {
        App.showToast('请修正表单中的错误', 'error');
        return;
    }

    const data = App.form.serialize(form);

    try {
        const response = await App.api.put(`/api/categories/${categoryId}`, data);

        if (response.success) {
            App.showToast('分类更新成功', 'success');
            App.modal.hide();
            setTimeout(() => location.reload(), 500);
        } else {
            App.showToast(response.error || '更新分类失败', 'error');
        }
    } catch (error) {
        console.error('更新分类错误:', error);
        App.showToast('更新分类失败', 'error');
    }
}

async function toggleCategory(categoryId) {
    try {
        const response = await App.api.post(`/api/categories/${categoryId}/toggle`);

        if (response.success) {
            App.showToast(response.message, 'success');
            setTimeout(() => location.reload(), 500);
        } else {
            App.showToast(response.error || '切换状态失败', 'error');
        }
    } catch (error) {
        console.error('切换状态错误:', error);
        App.showToast('切换状态失败', 'error');
    }
}

async function deleteCategory(categoryId) {
    const categoryData = window.categoryData.find(c => c.id === categoryId);
    const categoryName = categoryData ? categoryData.name : '未知';

    App.modal.confirm(
        `确定要删除分类 "${App.escapeHtml(categoryName)}" 吗？`,
        async () => {
            try {
                const response = await App.api.delete(`/api/categories/${categoryId}`);

                if (response.success) {
                    App.showToast('分类删除成功', 'success');
                    setTimeout(() => location.reload(), 500);
                } else {
                    App.showToast(response.error || '删除分类失败', 'error');
                }
            } catch (error) {
                console.error('删除分类错误:', error);
                App.showToast('删除分类失败', 'error');
            }
        },
        { title: '删除分类', danger: true }
    );
}

// ============================================================================
// Category Feeds Management
// ============================================================================

async function showCategoryFeeds(categoryId) {
    const categoryData = window.categoryData.find(c => c.id === categoryId);
    const categoryName = categoryData ? categoryData.name : '未知';

    // Update modal title
    document.getElementById('category-feeds-title').textContent =
        `"${App.escapeHtml(categoryName)}" 的订阅源`;

    // Show loading state
    document.getElementById('category-feeds-body').innerHTML = '<p class="empty-state">加载中...</p>';
    document.getElementById('category-feeds-modal').style.display = 'flex';

    try {
        const response = await App.api.get(`/api/categories/${categoryId}/feeds`);

        if (response.success) {
            const feeds = response.data.feeds || [];
            const total = response.data.total || 0;

            if (feeds.length === 0) {
                document.getElementById('category-feeds-body').innerHTML = `
                    <div class="empty-state">
                        <p>该分类下暂无订阅源</p>
                        <p style="margin-top: 1rem;">
                            <a href="{{ url_for('feeds') }}" class="btn btn-primary btn-small">前往订阅源管理</a>
                        </p>
                    </div>
                `;
            } else {
                let feedsHtml = `<p style="margin-bottom: 1rem; color: var(--text-muted);">共 ${total} 个订阅源：</p>`;
                feedsHtml += '<div style="display: flex; flex-direction: column; gap: 0.75rem;">';

                feeds.forEach(feed => {
                    feedsHtml += `
                        <div style="padding: 0.75rem; background-color: var(--bg-color); border-radius: 0.375rem; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong style="color: var(--text-color);">${App.escapeHtml(feed.name || feed.url)}</strong>
                                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                                    ${App.escapeHtml(feed.url.length > 60 ? feed.url.substring(0, 60) + '...' : feed.url)}
                                </div>
                            </div>
                            <span class="feed-status ${feed.enabled ? 'enabled' : 'disabled'}" style="font-size: 0.75rem;">
                                ${feed.enabled ? '已启用' : '已禁用'}
                            </span>
                        </div>
                    `;
                });

                feedsHtml += '</div>';
                document.getElementById('category-feeds-body').innerHTML = feedsHtml;
            }
        } else {
            document.getElementById('category-feeds-body').innerHTML = `
                <div class="empty-state">
                    <p style="color: var(--error-color);">${App.escapeHtml(response.error || '加载失败')}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('加载分类订阅源错误:', error);
        document.getElementById('category-feeds-body').innerHTML = `
            <div class="empty-state">
                <p style="color: var(--error-color);">加载失败</p>
            </div>
        `;
    }
}

function hideCategoryFeedsModal() {
    document.getElementById('category-feeds-modal').style.display = 'none';
}

// ============================================================================
// Feed Category Assignment (can be called from feeds page)
// ============================================================================

async function showFeedCategoriesModal(feedId, feedName) {
    // Get current categories for this feed
    try {
        const response = await App.api.get(`/api/feeds/${feedId}/categories`);
        const allCategories = window.categoryData || [];
        const currentCategoryIds = (response.success && response.data) ?
            response.data.map(c => c.id) : [];

        let content = `
            <form id="feed-categories-form" onsubmit="handleFeedCategoriesUpdate(event, ${feedId}, '${App.escapeHtml(feedName)}')">
                <p style="margin-bottom: 1rem; color: var(--text-muted);">为订阅源选择分类（可多选）：</p>
                <div class="form-group">
                    <div style="display: flex; flex-direction: column; gap: 0.5rem; max-height: 300px; overflow-y: auto;">
        `;

        if (allCategories.length === 0) {
            content += `<p class="empty-state">暂无可用分类，请先创建分类</p>`;
        } else {
            allCategories.forEach(category => {
                const isChecked = currentCategoryIds.includes(category.id);
                content += `
                    <label style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; background-color: var(--bg-color); border-radius: 0.375rem; cursor: pointer;">
                        <input type="checkbox" name="category_ids" value="${category.id}" ${isChecked ? 'checked' : ''}>
                        <span class="category-icon-small" style="background-color: ${category.color || '#64748b'};">
                            ${App.escapeHtml(category.icon || '📁')}
                        </span>
                        <span>${App.escapeHtml(category.name)}</span>
                    </label>
                `;
            });
        }

        content += `
                    </div>
                </div>
                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" onclick="App.modal.hide()">取消</button>
                    <button type="submit" class="btn btn-primary" ${allCategories.length === 0 ? 'disabled' : ''}>保存</button>
                </div>
            </form>
        `;

        App.modal.show(`管理分类 - ${App.escapeHtml(feedName)}`, content);
    } catch (error) {
        console.error('加载分类错误:', error);
        App.showToast('加载分类失败', 'error');
    }
}

async function handleFeedCategoriesUpdate(event, feedId, feedName) {
    event.preventDefault();
    const form = event.target;

    // Get selected category IDs
    const selectedCheckboxes = form.querySelectorAll('input[name="category_ids"]:checked');
    const categoryIds = Array.from(selectedCheckboxes).map(cb => parseInt(cb.value));

    try {
        const response = await App.api.put(`/api/feeds/${feedId}/categories`, {
            category_ids: categoryIds
        });

        if (response.success) {
            App.showToast(`已为 "${App.escapeHtml(feedName)}" 设置 ${categoryIds.length} 个分类`, 'success');
            App.modal.hide();
            setTimeout(() => location.reload(), 500);
        } else {
            App.showToast(response.error || '设置分类失败', 'error');
        }
    } catch (error) {
        console.error('设置分类错误:', error);
        App.showToast('设置分类失败', 'error');
    }
}

// ============================================================================
// Close category feeds modal on escape key
// ============================================================================

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        hideCategoryFeedsModal();
    }
});

// Close category feeds modal on overlay click
document.getElementById('category-feeds-modal').addEventListener('click', function(e) {
    if (e.target === this) {
        hideCategoryFeedsModal();
    }
});
