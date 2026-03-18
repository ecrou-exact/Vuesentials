const PaginationComponent = {
    props: {
        currentPage: {
            type: Number,
            required: true
        },
        totalPages: {
            type: Number,
            required: true
        }
    },
    emits: ['change-page'],
    delimiters: ['[[', ']]'],
    setup(props, { emit }) {
        const goToPage = (page) => {
            if (page >= 1 && page <= props.totalPages) {
                emit('change-page', page);
            }
        };

        const getPaginationRange = () => {
            const delta = 2;
            const left = props.currentPage - delta;
            const right = props.currentPage + delta + 1;
            const range = [];

            for (let i = 1; i <= props.totalPages; i++) {
                if (i == 1 || i == props.totalPages || (i >= left && i < right)) {
                    range.push(i);
                } else if (range[range.length - 1] !== '...') {
                    range.push('...');
                }
            }

            return range;
        };

        return {
            goToPage,
            getPaginationRange
        };
    },
    template: `
    <nav aria-label="Pagination" v-if="totalPages > 1" class="mb-4">
        <ul class="pagination justify-content-center">
            <!-- Previous Button -->
            <li class="page-item" :class="{ disabled: currentPage === 1 }">
                <button 
                    class="page-link"
                    @click="goToPage(currentPage - 1)"
                    :disabled="currentPage === 1"
                    style="border-radius: 0.625rem 0 0 0.625rem;">
                    <i class="fa-solid fa-chevron-left"></i>
                    <span class="ms-2 d-none d-sm-inline">Previous</span>
                </button>
            </li>

            <!-- Page Numbers -->
            <li v-for="(page, index) in getPaginationRange()" 
                :key="index"
                class="page-item"
                :class="{ active: page === currentPage, disabled: page === '...' }">
                <button 
                    v-if="page !== '...'"
                    class="page-link"
                    @click="goToPage(page)"
                    style="border-radius: 0.625rem; margin: 0 2px;">
                    [[ page ]]
                </button>
                <span v-else class="page-link" style="background: none; border: none; cursor: default;">
                    ...
                </span>
            </li>

            <!-- Next Button -->
            <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                <button 
                    class="page-link"
                    @click="goToPage(currentPage + 1)"
                    :disabled="currentPage === totalPages"
                    style="border-radius: 0 0.625rem 0.625rem 0;">
                    <span class="d-none d-sm-inline">Next</span>
                    <i class="fa-solid fa-chevron-right ms-2"></i>
                </button>
            </li>
        </ul>
    </nav>
    `
};

export default PaginationComponent;