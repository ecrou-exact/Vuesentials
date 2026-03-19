const ComponentMarkdownDisplay = {
    props: {
        content: { type: String, default: '' },
        title: { type: String, default: '' }
    },
    setup(props) {
        const containerRef = Vue.ref(null);

        Vue.onMounted(() => {
            renderMarkdown();
        });

        Vue.watch(() => props.content, () => {
            renderMarkdown();
        });

        const renderMarkdown = () => {
            if (!containerRef.value || !window.marked) return;

            window.marked.setOptions({
                breaks: true,
                gfm: true,
                headerIds: true
            });

            const html = window.marked.parse(props.content);
            

            if (containerRef.value) {
                containerRef.value.innerHTML = html;
                
                if (window.hljs) {
                    containerRef.value.querySelectorAll('pre code').forEach(block => {
                        window.hljs.highlightElement(block);
                    });
                }
            }
        };

        return { containerRef };
    },
    template: `
        <div class="markdown-display-wrapper">
            <div v-if="title" class="markdown-display-title">{{ title }}</div>
            <div ref="containerRef" class="markdown-display-content"></div>
        </div>
    `
};

export default ComponentMarkdownDisplay;