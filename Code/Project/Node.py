class Node:
    f_x = 0
    f_y = 0
    f_z = 0
    m_x = 0
    m_y = 0
    m_z = 0
    d_x = 0
    d_y = 0
    d_z = 0
    t_x = None
    t_y = None
    t_z = None
    r_x = None
    r_y = None
    r_z = None

    def __init__(self, id, p_x, p_y, p_z):
        self.id = id
        self.p_x = p_x
        self.p_y = p_y
        self.p_z = p_z

        return None
