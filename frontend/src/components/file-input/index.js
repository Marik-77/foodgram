import { useState, useEffect, useRef } from 'react'
import styles from './styles.module.css'
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
  const fileInputRef = useRef(null)

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
      {label && <span className={styles.label}>{label}</span>}
      <div className={styles.controls}>
        {reading ? (
          <span className={styles.reading}>Обработка файла…</span>
        ) : (
          <>
            {/*
              Нативный input без скрытия: браузеры (особенно мобильные) часто блокируют
              кастомные кнопки + opacity:0 / display:none. Папки на сервере для этого не нужны.
            */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg,image/jpg,image/heic,image/heif,.heic,.heif"
              disabled={reading}
              className={styles.nativeInput}
              onChange={(e) => {
                const f = e.target.files[0]
                getBase64(f)
              }}
            />
            <p className={styles.hint}>
              Нажмите кнопку выбора файла выше. На сервер данные уйдут только после «Создать рецепт».
            </p>
          </>
        )}
      </div>
      {currentFile && (
        <div
          className={styles.image}
          style={{
            backgroundImage: `url(${currentFile})`,
          }}
          onClick={() => {
            onChange(null)
            setCurrentFile(null)
            if (fileInputRef.current) {
              fileInputRef.current.value = null
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
