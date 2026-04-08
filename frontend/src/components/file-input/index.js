import { useState, useEffect, useRef } from 'react'
import styles from './styles.module.css'
import { Button } from '../index'
import cn from 'classnames'
import Icons from '../icons'

const ALLOWED_MIME = ['image/png', 'image/jpeg', 'image/jpg', 'image/pjpeg', 'image/heic', 'image/heif']

function isAllowedImageType(file) {
  if (!file || !file.type) {
    const n = (file && file.name) || ''
    return /\.(jpe?g|png|heic|heif)$/i.test(n)
  }
  return ALLOWED_MIME.includes(file.type.toLowerCase())
}

const FileInput = ({
  label,
  onChange,
  file: fileProp,
  className,
  fileSize,
}) => {
  const controlled = fileProp !== undefined
  const [currentFile, setCurrentFile] = useState(() =>
    controlled ? fileProp : null
  )
  const [reading, setReading] = useState(false)
  const fileInput = useRef(null)

  useEffect(() => {
    if (!controlled) {
      return
    }
    setCurrentFile(fileProp)
  }, [controlled, fileProp])

  const getBase64 = (file) => {
    if (!file) {
      return
    }
    const reader = new FileReader()

    if (fileSize && file.size / 1000 > fileSize) {
      return alert(`Загрузите файл размером не более ${fileSize / 1000} Мб`)
    }
    if (!isAllowedImageType(file)) {
      return alert(
        `Нужен файл PNG, JPEG или HEIC. Тип: ${file.type || 'не определён'}, имя: ${file.name || '—'}`
      )
    }
    setReading(true)
    reader.readAsDataURL(file)
    reader.onload = function () {
      setCurrentFile(reader.result)
      onChange(reader.result)
      setReading(false)
    }
    reader.onerror = function (error) {
      console.log('Error: ', error)
      setReading(false)
    }
  }

  return (
    <div className={cn(styles.container, className)}>
      {label && (
        <label className={styles.label}>
          {label}
        </label>
      )}
      <input
        className={styles.fileInput}
        type="file"
        accept="image/png,image/jpeg,image/jpg,image/heic,image/heif,.heic,.heif"
        ref={fileInput}
        onChange={(e) => {
          const f = e.target.files[0]
          getBase64(f)
        }}
      />
      <Button
        clickHandler={() => {
          fileInput.current.click()
        }}
        className={styles.button}
        type="button"
        disabled={reading}
        title="Файл уходит на сервер при нажатии «Создать рецепт» или «Сохранить», отдельного запроса при выборе файла нет."
      >
        {reading ? 'Обработка файла…' : 'Выбрать файл'}
      </Button>
      {currentFile && (
        <div
          className={styles.image}
          style={{
            backgroundImage: `url(${currentFile})`,
          }}
          onClick={() => {
            onChange(null)
            setCurrentFile(null)
            if (fileInput.current) {
              fileInput.current.value = null
            }
          }}
        >
          <div className={styles.imageOverlay}>
            <Icons.ReceiptDelete />
          </div>
        </div>
      )}
    </div>
  )
}

export default FileInput
