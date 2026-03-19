const ComponentCodeHighlight = {
    props: ['content', 'lang'],
    delimiters: ['[[', ']]'],
    mounted() {
        this.highlightCode();
    },
    updated() {
        this.highlightCode();
    },
    methods: {
        highlightCode() {
            const el = this.$refs.codeBlock;
            if (el && window.hljs) {
                el.removeAttribute('data-highlighted');
                window.hljs.highlightElement(el);
            }
        }
    },
    template: `
        <pre><code 
            ref="codeBlock" 
            :class="'language-' + lang" 
            v-text="content"></code></pre>
    `
};

export default ComponentCodeHighlight;