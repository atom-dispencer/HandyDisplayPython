static PyObject *
SpiDev_xfer(SpiDevObject *self, PyObject *args)
{
	uint16_t ii, len;
	int status;
	uint16_t delay_usecs = 0;
	uint32_t speed_hz = 0;
	uint8_t bits_per_word = 0;
	PyObject *obj;
	PyObject *seq;
	struct spi_ioc_transfer xfer;
	memset(&xfer, 0, sizeof(xfer));
	uint8_t *txbuf, *rxbuf;
	char	wrmsg_text[4096];

	if (!PyArg_ParseTuple(args, "O|IHB:xfer", &obj, &speed_hz, &delay_usecs, &bits_per_word))
		return NULL;

	seq = PySequence_Fast(obj, "expected a sequence");
	if (!seq) {
		PyErr_SetString(PyExc_TypeError, wrmsg_list0);
		return NULL;
	}

	len = PySequence_Fast_GET_SIZE(seq);
	if (len <= 0) {
		Py_DECREF(seq);
		PyErr_SetString(PyExc_TypeError, wrmsg_list0);
		return NULL;
	}

	if (len > SPIDEV_MAXPATH) {
		snprintf(wrmsg_text, sizeof(wrmsg_text) - 1, wrmsg_listmax, SPIDEV_MAXPATH);
		PyErr_SetString(PyExc_OverflowError, wrmsg_text);
		Py_DECREF(seq);
		return NULL;
	}

	txbuf = malloc(sizeof(__u8) * len);
	rxbuf = malloc(sizeof(__u8) * len);

#ifdef SPIDEV_SINGLE
	xferptr = (struct spi_ioc_transfer*) malloc(sizeof(struct spi_ioc_transfer) * len);

	for (ii = 0; ii < len; ii++) {
		PyObject *val = PySequence_Fast_GET_ITEM(seq, ii);
#if PY_MAJOR_VERSION < 3
		if (PyInt_Check(val)) {
			txbuf[ii] = (__u8)PyInt_AS_LONG(val);
		} else
#endif
		{
			if (PyLong_Check(val)) {
				txbuf[ii] = (__u8)PyLong_AS_LONG(val);
			} else {
				snprintf(wrmsg_text, sizeof(wrmsg_text) - 1, wrmsg_val, val);
				PyErr_SetString(PyExc_TypeError, wrmsg_text);
				free(xferptr);
				free(txbuf);
				free(rxbuf);
				Py_DECREF(seq);
				return NULL;
			}
		}
		xferptr[ii].tx_buf = (unsigned long)&txbuf[ii];
		xferptr[ii].rx_buf = (unsigned long)&rxbuf[ii];
		xferptr[ii].len = 1;
		xferptr[ii].delay_usecs = delay;
		xferptr[ii].speed_hz = speed_hz ? speed_hz : self->max_speed_hz;
		xferptr[ii].bits_per_word = bits_per_word ? bits_per_word : self->bits_per_word;
#ifdef SPI_IOC_WR_MODE32
		xferptr[ii].tx_nbits = 0;
#endif
#ifdef SPI_IOC_RD_MODE32
		xferptr[ii].rx_nbits = 0;
#endif
	}

	status = ioctl(self->fd, SPI_IOC_MESSAGE(len), xferptr);
	free(xferptr);
	if (status < 0) {
		PyErr_SetFromErrno(PyExc_IOError);
		free(txbuf);
		free(rxbuf);
		Py_DECREF(seq);
		return NULL;
	}
#else
	for (ii = 0; ii < len; ii++) {
		PyObject *val = PySequence_Fast_GET_ITEM(seq, ii);
#if PY_MAJOR_VERSION < 3
		if (PyInt_Check(val)) {
			txbuf[ii] = (__u8)PyInt_AS_LONG(val);
		} else
#endif
		{
			if (PyLong_Check(val)) {
				txbuf[ii] = (__u8)PyLong_AS_LONG(val);
			} else {
				snprintf(wrmsg_text, sizeof(wrmsg_text) - 1, wrmsg_val, val);
				PyErr_SetString(PyExc_TypeError, wrmsg_text);
				free(txbuf);
				free(rxbuf);
				Py_DECREF(seq);
				return NULL;
			}
		}
	}

	if (PyTuple_Check(obj)) {
		Py_DECREF(seq);
		seq = PySequence_List(obj);
	}

	xfer.tx_buf = (unsigned long)txbuf;
	xfer.rx_buf = (unsigned long)rxbuf;
	xfer.len = len;
	xfer.delay_usecs = delay_usecs;
	xfer.speed_hz = speed_hz ? speed_hz : self->max_speed_hz;
	xfer.bits_per_word = bits_per_word ? bits_per_word : self->bits_per_word;
#ifdef SPI_IOC_WR_MODE32
	xfer.tx_nbits = 0;
#endif
#ifdef SPI_IOC_RD_MODE32
	xfer.rx_nbits = 0;
#endif

	status = ioctl(self->fd, SPI_IOC_MESSAGE(1), &xfer);
	if (status < 0) {
		PyErr_SetFromErrno(PyExc_IOError);
		free(txbuf);
		free(rxbuf);
		Py_DECREF(seq);
		return NULL;
	}
#endif

	for (ii = 0; ii < len; ii++) {
		PyObject *val = PyLong_FromLong((long)rxbuf[ii]);
		PySequence_SetItem(seq, ii, val);
		Py_DECREF(val); // PySequence_SetItem does not steal reference, must Py_DECREF(val)
	}

	// WA:
	// in CS_HIGH mode CS isn't pulled to low after transfer, but after read
	// reading 0 bytes doesnt matter but brings cs down
	// tomdean:
	// Stop generating an extra CS except in mode CS_HOGH
	if (self->read0 && (self->mode & SPI_CS_HIGH)) status = read(self->fd, &rxbuf[0], 0);

	free(txbuf);
	free(rxbuf);

	if (PyTuple_Check(obj)) {
		PyObject *old = seq;
		seq = PySequence_Tuple(seq);
		Py_DECREF(old);
	}

	return seq;
}