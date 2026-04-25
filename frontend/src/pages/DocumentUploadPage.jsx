import { useState } from 'react'
import api from '../services/api'

function DocumentUploadPage() {
  const [file, setFile] = useState(null)
  const [docType, setDocType] = useState('national_id')
  const [caseId, setCaseId] = useState('')
  const [message, setMessage] = useState('')

  async function submit(e) {
    e.preventDefault()
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    formData.append('doc_type', docType)
    if (caseId) formData.append('case_id', caseId)

    try {
      const { data } = await api.post('/beneficiary/documents/upload', formData)
      setMessage(`Document uploaded. ID ${data.document_id}`)
    } catch (err) {
      setMessage(err.response?.data?.error || 'Upload failed')
    }
  }

  return (
    <section>
      <h1>Document Upload</h1>
      <form onSubmit={submit} className="form-grid">
        <input placeholder="Case ID (optional)" value={caseId} onChange={(e) => setCaseId(e.target.value)} />
        <input placeholder="Document Type" value={docType} onChange={(e) => setDocType(e.target.value)} />
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button>Upload</button>
      </form>
      <p>{message}</p>
    </section>
  )
}

export default DocumentUploadPage
