import ExamPanel from '../components/ExamPanel'

export default function ExamPage({ subject, onFinish }) {
  return <ExamPanel subject={subject} onFinish={onFinish} />
}
