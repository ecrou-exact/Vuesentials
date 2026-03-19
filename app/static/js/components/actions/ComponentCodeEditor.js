const CodeMirrorEditor = {
    props: {
        modelValue: { type: String, default: '' },
        mode: { type: String, default: 'javascript' }, 
        theme: { type: String, default: 'monokai' },
        height: { type: String, default: '450px' },
        name: { type: String, required: true },
        placeholder: { type: String, default: 'Code goes here' } 
    },
    setup(props) {
        const textareaRef = Vue.ref(null);
        const rootRef = Vue.ref(null); 
        let editor = null;
        
        Vue.onMounted(() => {
            if (!textareaRef.value || !window.CodeMirror) return;

            editor = CodeMirror.fromTextArea(textareaRef.value, {
                lineNumbers: true,
                mode: props.mode,
                theme: props.theme,
                lineWrapping: true,
                indentUnit: 4,
                tabSize: 4,
                autoCloseBrackets: true, 
                matchBrackets: true,     
                spellcheck: false,     
                autofocus: false,
                placeholder: props.placeholder
            });

            editor.setSize('100%', props.height);
            editor.setValue(props.modelValue || '');

            editor.on('change', () => {
                const content = editor.getValue();
                const hiddenInput = document.querySelector(`input[name="${props.name}"]`);
                if (hiddenInput) {
                    hiddenInput.value = content;
                }
            });

            setTimeout(() => editor.refresh(), 100);
        });

        return { textareaRef, rootRef };
    },
    template: `
        <div ref="rootRef" class="codemirror-container border rounded shadow-sm">
            <textarea ref="textareaRef"></textarea>
        </div>
    `
};

export default CodeMirrorEditor;