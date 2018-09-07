#include <Python.h>

typedef struct {
    PyObject_HEAD
    /* Type-specific fields go here. */
    int spacer;
} CustomObject;


/*
 * forward declaration of indication() to send packets downstream in case the
 * response() function wants to send some.
 */
static void
indication(CustomObject *self, void *buf, int len);


static void
response(CustomObject *self, void *buf, int len)
{
    /*
        This function is called for each upstream packet from the TCPServer.
    */

    printf("0x%08lX:response got the buffer, %d bytes\n",
        (long)self, len
        );

    /* send the data back just for fun */
    indication(self, buf, len);
}


static void
indication(CustomObject *self, void *buf, int len)
{
    /*
        This function is called to send a packet downstream to the TCPServer
        and is the equivalent to calling self.indication(PDU(bytes(buf)))
    */

    printf("0x%08lX:indication\n", (long)self);

    PyObject *pdu = NULL;
    PyObject *pdu_data = NULL;
    PyObject *pdu_data_name = NULL;

    /* get the PDU class */
    PyObject *module = PyImport_ImportModule("bacpypes.pdu");
    PyObject *module_dict = PyModule_GetDict(module);
    PyObject *pdu_class = PyDict_GetItemString(module_dict, "PDU");

    /* build a PDU object */
    pdu = PyObject_CallFunction(pdu_class, "");

    /* build a bytes/buffer object */
    pdu_data = Py_BuildValue("y#", (const char *)buf, len);

    /* set the pduData attribute */
    pdu_data_name = PyUnicode_FromString("pduData");
    PyObject_SetAttr(pdu, pdu_data_name, pdu_data);
    Py_DECREF(pdu_data_name);

    /* call the StreamClient.indication() function */
    PyObject *result = PyObject_CallMethod((PyObject *)self, "indication", "O", pdu);

    Py_DECREF(result);
    Py_DECREF(pdu_data);
    Py_DECREF(pdu);
}


static int
Custom_init(CustomObject *self, PyObject *args, PyObject *kwds)
{
    /*
        Custom class initializer.
    */

    printf("0x%08lX:Custom_init\n", (long)self);

    /* is this still necessary? */
    self->spacer = 0;

    return 0;
}


static PyObject *
Custom_response(CustomObject *self, PyObject *args)
{
    /*
        This function is called when there is an upstream packet from the
        TCPServer.  It assumes that it is being called with a single
        PDU instance where the pduData is a bytearray.
    */

    printf("0x%08lX:Custom_response\n", (long)self);

    PyObject    *pdu = NULL;
    PyObject    *pdu_data = NULL;
    PyObject    *pdu_data_name = NULL;
    Py_buffer   pdu_data_buffer;

    /* get the pdu object from the function arguments */
    if (!PyArg_ParseTuple(args, "O", &pdu)) {
        return NULL;
    }

    /* get the pduData attribute from the pdu */
    pdu_data_name = PyUnicode_FromString("pduData");
    pdu_data = PyObject_GetAttr(pdu, pdu_data_name);
    Py_DECREF(pdu_data_name);
    if (!pdu_data) {
        return NULL;
    }

    /* make sure it is a bytearray and supports the buffer protocol */
    if (!PyByteArray_Check(pdu_data)) {
        Py_DECREF(pdu_data);
        return NULL;
    }
    if (!PyObject_CheckBuffer(pdu_data)) {
        Py_DECREF(pdu_data);
        return NULL;
    }

    /* get a contiguous, read-only buffer */
    if (PyObject_GetBuffer(pdu_data, &pdu_data_buffer, PyBUF_CONTIG_RO) == 0) {
        response(self, pdu_data_buffer.buf, pdu_data_buffer.len);
        PyBuffer_Release(&pdu_data_buffer);
    } else {
        /* problems getting buffer */
    }

    Py_DECREF(pdu_data);

    Py_RETURN_NONE;
}

static PyMethodDef Custom_methods[] = {
    {"response", (PyCFunction) Custom_response, METH_VARARGS, "upstream data"},
    {NULL}
};

static PyTypeObject CustomType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "custom.Custom",
    .tp_doc = "Custom objects",
    .tp_basicsize = sizeof(CustomObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc)Custom_init,
    .tp_methods = Custom_methods,
};

static PyModuleDef custommodule = {
    PyModuleDef_HEAD_INIT,
    .m_name = "custom",
    .m_doc = "Example module that creates an extension type.",
    .m_size = -1,
};

PyMODINIT_FUNC
PyInit_custom(void)
{
    /*
        Initialize the custom module and add the Custom type.
    */

    PyObject *m;
    if (PyType_Ready(&CustomType) < 0)
        return NULL;

    m = PyModule_Create(&custommodule);
    if (m == NULL)
        return NULL;

    Py_INCREF(&CustomType);
    PyModule_AddObject(m, "Custom", (PyObject *) &CustomType);
    return m;
}
