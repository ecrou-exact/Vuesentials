const ComponentMarkdownEditor = {
    props: {
        modelValue: { type: String, default: '' },
        name: String,
        height: { type: String, default: '400px' }
    },
    setup(props) {
        const textareaRef = Vue.ref(null);
        let editor = null;

        Vue.onMounted(() => {
            if (textareaRef.value && window.EasyMDE) {
                textareaRef.value.value = props.modelValue || '';
                
                editor = new EasyMDE({
                    element: textareaRef.value,
                    spellChecker: false,
                    autoDownloadFontAwesome: false,
                    toolbar: [
                        'bold',
                        'italic',
                        'heading',
                        '|',
                        'quote',
                        'unordered-list',
                        'ordered-list',
                        '|',
                        'link',
                        'image',
                        'code',
                        'horizontal-rule',
                        '|',
                        'preview',
                        'side-by-side',
                        'fullscreen',
                        '|',
                        'guide'
                    ],
                    status: ['lines', 'words', 'cursor'],
                    lineWrapping: true,
                    indentWithTabs: false,
                    tabSize: 4
                });

                editor.codemirror.setSize('100%', props.height);

                editor.codemirror.on('change', () => {
                    const hiddenInput = document.querySelector(`input[name="${props.name}"]`);
                    if (hiddenInput) {
                        hiddenInput.value = editor.value();
                    }
                });

                setTimeout(() => editor.codemirror.refresh(), 100);
            }
        });

        Vue.watch(() => props.modelValue, (newVal) => {
            if (editor && newVal) {
                const currentVal = editor.value();
                if (newVal !== currentVal) {
                    editor.value(newVal);
                }
            }
        });

        return { textareaRef };
    },
    template: `
        <div class="markdown-editor-wrapper border rounded-3 overflow-hidden">
            <textarea ref="textareaRef"></textarea>
        </div>
    `
};

export default ComponentMarkdownEditor;