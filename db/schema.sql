--
-- PostgreSQL database dump
--

--
-- TOC entry 218 (class 1259 OID 16441)
--

CREATE TABLE public.precios (
    id_producto integer NOT NULL,
    precio_neto numeric,
    costo_neto numeric,
    utilidad_neta numeric
);



--
-- TOC entry 217 (class 1259 OID 16432)
--

CREATE TABLE public.productos (
    id_producto integer NOT NULL,
    nombre text NOT NULL,
    stock integer
);



--
-- TOC entry 222 (class 1259 OID 16484)
--

ALTER TABLE public.productos ALTER COLUMN id_producto ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.productos_id_producto_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 221 (class 1259 OID 16482)
--

CREATE SEQUENCE public.ventas_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 219 (class 1259 OID 16453)
--

CREATE TABLE public.ventas (
    id_venta integer DEFAULT nextval('public.ventas_id_seq'::regclass) NOT NULL,
    fecha date,
    forma_pago text,
    monto_total numeric,
    total_productos integer
);



--
-- TOC entry 220 (class 1259 OID 16460)
--

CREATE TABLE public.ventas_producto (
    id_venta integer,
    id_producto integer,
    cantidad integer,
    monto_producto numeric
);



--
-- TOC entry 4761 (class 2606 OID 16447)
--

ALTER TABLE ONLY public.precios
    ADD CONSTRAINT precios_pkey PRIMARY KEY (id_producto);


--
-- TOC entry 4757 (class 2606 OID 16438)
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_pkey PRIMARY KEY (id_producto);


--
-- TOC entry 4759 (class 2606 OID 16440)
--

ALTER TABLE ONLY public.productos
    ADD CONSTRAINT productos_producto_key UNIQUE (nombre);


--
-- TOC entry 4763 (class 2606 OID 16459)
--

ALTER TABLE ONLY public.ventas
    ADD CONSTRAINT ventas_pkey PRIMARY KEY (id_venta);


--
-- TOC entry 4764 (class 2606 OID 16448)
--

ALTER TABLE ONLY public.precios
    ADD CONSTRAINT precios_id_producto_fkey FOREIGN KEY (id_producto) REFERENCES public.productos(id_producto);


--
-- TOC entry 4765 (class 2606 OID 16470)
--

ALTER TABLE ONLY public.ventas_producto
    ADD CONSTRAINT ventas_producto_id_producto_fkey FOREIGN KEY (id_producto) REFERENCES public.productos(id_producto);


--
-- TOC entry 4766 (class 2606 OID 16465)
--

ALTER TABLE ONLY public.ventas_producto
    ADD CONSTRAINT ventas_producto_id_venta_fkey FOREIGN KEY (id_venta) REFERENCES public.ventas(id_venta);


--
-- PostgreSQL database dump complete
--

