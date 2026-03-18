const ComponentFilterBar = {
    props: {
        apiEndpoint: { type: String, required: true },
        placeholder: { type: String, default: 'Search components...' },
        autoFetch: { type: Boolean, default: true },
        csrfToken: { type: String, default: '' },
    },
    emits: ['update:results', 'loading'],
    delimiters: ['[[', ']]'],
    setup(props, { emit }) {
        const searchQuery = Vue.ref('');
        const searchField = Vue.ref('all');
        const sortBy = Vue.ref('newest');
        const categoryFilter = Vue.ref('');
        const difficultyFilter = Vue.ref('');
        const searchIsLoading = Vue.ref(false);
        const categories = Vue.ref([]);
        const difficulties = Vue.ref(['Beginner', 'Intermediate', 'Advanced']);
        
        const hasActiveFilters = Vue.computed(() => {
            return searchQuery.value.trim() !== '' || 
                   categoryFilter.value !== '' || 
                   difficultyFilter.value !== '';
        });

        Vue.watch(searchQuery, (newVal) => {
            if (newVal.trim() === '') fetchComponents(1);
        });

        const fetchCategories = async () => {
            try {
                const res = await fetch('/components/categories');
                const data = await res.json();
                categories.value = data.categories || [];
            } catch (e) {
                console.error("Categories fetch error:", e);
            }
        };

        const fetchComponents = async (page = 1) => {
            searchIsLoading.value = true;
            emit('loading', true);

            const params = new URLSearchParams();
            params.append('page', page.toString());
            params.append('search', searchQuery.value || '');
            params.append('search_field', searchField.value);
            params.append('sort_by', sortBy.value);

            if (categoryFilter.value !== '') {
                params.append('category', categoryFilter.value);
            }

            if (difficultyFilter.value !== '') {
                params.append('difficulty', difficultyFilter.value);
            }

            try {
                const url = `${props.apiEndpoint}?${params.toString()}`;
                const res = await fetch(url);
                const data = await res.json();
                
                emit('update:results', {
                    components: data.components || [],
                    total_pages: data.total_pages || 1,
                    total_components: data.total_components || 0,
                    current_page: page
                });
            } catch (error) {
                console.error("Fetch components error:", error);
            } finally {
                searchIsLoading.value = false;
                emit('loading', false);
            }
        };

        const clearSearch = () => {
            searchQuery.value = '';
        };

        const clearFilters = () => {
            searchQuery.value = '';
            searchField.value = 'all';
            sortBy.value = 'newest';
            categoryFilter.value = '';
            difficultyFilter.value = '';
            fetchComponents(1);
        };

        Vue.onMounted(() => {
            fetchCategories();
            if (props.autoFetch) fetchComponents(1);
        });

        return {
            searchQuery,
            searchField,
            sortBy,
            categoryFilter,
            difficultyFilter,
            searchIsLoading,
            categories,
            difficulties,
            hasActiveFilters,
            fetchComponents,
            clearSearch,
            clearFilters,
        };
    },
    template: `
    <div class="filter-bar-container">
        <div class="row g-3">
            <!-- Search Input -->
            <div class="col-md-6">
                <label class="filter-label">
                    <i class="fa-solid fa-magnifying-glass me-1"></i> Search
                </label>
                <div class="search-input-wrapper">
                    <i class="fa-solid fa-magnifying-glass"></i>
                    <input 
                        type="text"
                        v-model="searchQuery"
                        @keyup.enter="fetchComponents(1)"
                        class="form-control"
                        :placeholder="placeholder"
                        :disabled="searchIsLoading">
                    <button v-if="searchQuery && !searchIsLoading"
                            @click="clearSearch"
                            class="btn-clear">
                        <i class="fa-solid fa-circle-xmark"></i>
                    </button>
                </div>
            </div>

            <!-- Sort By -->
            <div class="col-md-3">
                <label class="filter-label">
                    <i class="fa-solid fa-arrow-down-up me-1"></i> Sort By
                </label>
                <select v-model="sortBy"
                        class="form-select"
                        @change="fetchComponents(1)"
                        :disabled="searchIsLoading">
                    <option value="newest">Newest First</option>
                    <option value="oldest">Oldest First</option>
                    <option value="most_viewed">Most Viewed</option>
                </select>
            </div>

            <!-- Clear Filters -->
            <div class="col-md-3 d-flex align-items-end">
                <button v-if="hasActiveFilters"
                        @click="clearFilters"
                        class="btn-clear-filters w-100">
                    <i class="fa-solid fa-xmark me-1"></i> Clear
                </button>
            </div>
        </div>

        <!-- Category & Difficulty -->
        <div class="row g-3 mt-1">
            <!-- Category Filter -->
            <div class="col-md-6">
                <label class="filter-label">
                    <i class="fa-solid fa-tag me-1"></i> Category
                </label>
                <select v-model="categoryFilter"
                        class="form-select"
                        @change="fetchComponents(1)"
                        :disabled="searchIsLoading">
                    <option value="">All Categories</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.name">
                        [[ cat.name ]]
                    </option>
                </select>
            </div>

            <!-- Difficulty Filter -->
            <div class="col-md-6">
                <label class="filter-label">
                    <i class="fa-solid fa-layer-group me-1"></i> Difficulty
                </label>
                <select v-model="difficultyFilter"
                        class="form-select"
                        @change="fetchComponents(1)"
                        :disabled="searchIsLoading">
                    <option value="">All Levels</option>
                    <option v-for="diff in difficulties" :key="diff" :value="diff.toLowerCase()">
                        [[ diff ]]
                    </option>
                </select>
            </div>
        </div>
    </div>
    `
};

export default ComponentFilterBar;